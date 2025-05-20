# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import traceback
from xml.dom.minidom import parseString
from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
import requests


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    gasto_flete_id = fields.Integer(
        'Gasto en Progress',
        help='Gasto del flete en Progress',
    )

    @api.multi
    def action_move_create(self):
        """
        Creates invoice related analytics and financial move lines
        """
        res = super().action_move_create()

        for inv in self:
            if inv.type == "in_invoice":
                proveedor = inv.partner_id

                if proveedor.vat == 'MXTGN940221973':
                    itinerario = inv.itinerary or False

                    if not itinerario:
                        raise ValidationError('El numero de itinerario es obligatorio \
                                  para el proveedor %s!' % proveedor.name)

                    if itinerario != 99999999:
                        tran_id = inv.number
                        analitica = inv.account_analytic_id.code

                        alm_progress = 0
                        if analitica.startswith('PRO-A'):
                            alm_progress = 1
                        elif analitica.startswith('PRO-B'):
                            alm_progress = 2
                        if analitica.startswith('PRO-D'):
                            alm_progress = 6
                        if analitica.startswith('PRO-F'):
                            alm_progress = 11

                        serealizado = str(itinerario) + ";" + str(tran_id) \
                            + ";" + str(alm_progress) + ";validate"

                        # gasto_flete = 0
                        # gasto_flete = self.actualiza_itinerario_progress(
                        #     serealizado)
                        # inv.gasto_flete_id = int(gasto_flete[0])
            # elif inv.type == "out_invoice":
            #    if not inv.sale_id.id:
            #        continue

            #    tran_id = inv.sale_id.name

            #    detalle_ser = ''
            #    for line in inv.invoice_line_ids:
            #        detalle_ser += str(line.product_id.numctrl_progress) \
            #            + ", " + str(line.quantity) + "|"

            #    res_ws = self.actualiza_pedido_progress(
            #        tran_id, detalle_ser, 1)

        return res

    @api.multi
    def button_gasto_flete(self):
        for inv in self:
            if inv.type == "in_invoice":
                proveedor = inv.partner_id

                if proveedor.vat == 'MXTGN940221973':
                    itinerario = inv.itinerary or False

                    if not itinerario:
                        raise ValidationError('El numero de itinerario es obligatorio \
                                  para el proveedor %s!' % proveedor.name)

                    if itinerario != 99999999:
                        tran_id = inv.number
                        analitica = inv.account_analytic_id.code

                        alm_progress = 0
                        if analitica.startswith('PRO-A'):
                            alm_progress = 1
                        elif analitica.startswith('PRO-B'):
                            alm_progress = 2
                        if analitica.startswith('PRO-D'):
                            alm_progress = 6
                        if analitica.startswith('PRO-F'):
                            alm_progress = 11

                        serealizado = str(itinerario) + ";" + str(tran_id) \
                            + ";" + str(alm_progress) + ";validate"

                        # gasto_flete = 0
                        # gasto_flete = self.actualiza_itinerario_progress(
                        #     serealizado)
                        # inv.gasto_flete_id = int(gasto_flete[0])

    def actualiza_itinerario_progress(self, serialized):
        """
        @params fdata : File.xml codification in base64
        """
        url = "http://148.244.148.218:8060/wsa/wsa1"

        msg = "<soapenv:Envelope xmlns:soapenv='http://schemas."
        msg += "xmlsoap.org/soap/envelope/' xmlns:urn='urn:services-progress"
        msg += "-com:deysy:wsagsf001w:wsagsf001'>"
        msg += "<soapenv:Header/>"
        msg += "<soapenv:Body>"
        msg += "<urn:Connect_wsagsf001>"
        msg += "<urn:userId>supervisor</urn:userId>"
        msg += "<urn:password>gierp</urn:password>"
        msg += "<urn:appServerInfo>?</urn:appServerInfo>"
        msg += "</urn:Connect_wsagsf001>"
        msg += "</soapenv:Body>"
        msg += "</soapenv:Envelope>"

        headers = {
            'content-type': "text/xml",
            'soapaction': "Connect_wsagsf001",
        }

        try:
            response = requests.request(
                "POST",
                url,
                data=msg,
                headers=headers
            )

            # print(response.text)

            resultados_mensaje = response.content
            dom = parseString(resultados_mensaje)
            nodo = dom.getElementsByTagName('UUID')
            token = nodo[0].firstChild.nodeValue

            # print(token)
            # print(serialized)
        except Exception as e:
            error = tools.ustr(traceback.format_exc())
            # # print error
            raise ValidationError('Ocurrio un error al firmarse en \
                                  Progress favor de notificar al \
                                  Administrador del sistema')

        msgrel = "<soapenv:Envelope xmlns:soapenv='http://schemas."
        msgrel += "xmlsoap.org/soap/envelope/' xmlns:urn='urn:services-progres"
        msgrel += "s-com:deysy:wsagsf001w:wsagsf001'>"
        msgrel += "<soapenv:Header>"
        msgrel += "<urn:wsagsf001ID>"
        msgrel += "<urn:UUID>" + token + "</urn:UUID>"
        msgrel += "</urn:wsagsf001ID>"
        msgrel += "</soapenv:Header>"
        msgrel += "<soapenv:Body>"
        msgrel += "<urn:Release_wsagsf001/>"
        msgrel += "</soapenv:Body>"
        msgrel += "</soapenv:Envelope>"

        headrel = {
            'content-type': "text/xml",
            'soapaction': "Release_wsagsf001",
        }

        # ejecuta query
        headers = {
            'content-type': "text/xml",
            'soapaction': "wsagsf001",
        }

        msg = "<soapenv:Envelope xmlns:soapenv='http://schemas."
        msg += "xmlsoap.org/soap/envelope/' xmlns:urn='urn:services-progress-"
        msg += "com:deysy:wsagsf001w:wsagsf001'>"
        msg += "<soapenv:Header>"
        msg += "<urn:wsagsf001ID>"
        msg += "<urn:UUID><![CDATA[" + token + "]]></urn:UUID>"
        msg += "</urn:wsagsf001ID>"
        msg += "</soapenv:Header>"
        msg += "<soapenv:Body>"
        msg += "<urn:wsagsf001w>"
        msg += "<urn:pSERIALIZADO>" + serialized + "</urn:pSERIALIZADO>"
        msg += "</urn:wsagsf001w>"
        msg += "</soapenv:Body>"
        msg += "</soapenv:Envelope>"

        try:
            response = requests.request(
                "POST",
                url,
                data=msg,
                headers=headers
            )

            # print(response.text)
            resultados_mensaje = response.content
            dom = parseString(resultados_mensaje)
            nodo = dom.getElementsByTagName('pRESPONSE')
            res = nodo[0].firstChild.nodeValue
            mensaje = res.split('|')
        except Exception as e:
            response = requests.request(
                "POST",
                url,
                data=msgrel,
                headers=headrel
            )
            error = tools.ustr(traceback.format_exc())
            raise ValidationError('Ocurrio un error al enviar Información \
                                  a Progress favor de notificar \
                                  al Administrador del sistema')

        response = requests.request(
            "POST",
            url,
            data=msgrel,
            headers=headrel
        )

        if mensaje[0] == 'ERROR':
            raise ValidationError('Ocurrio un error del lado de OpenEdge \
                                  OpenEdge dice: ' + mensaje[1])

        mensaje.pop(0)
        return mensaje

    def actualiza_pedido_progress(self, folio, serializado, creacancela):
        """
        @params fdata : File.xml codification in  base64
        """
        url = "http://148.244.148.218:8060/wsa/wsa1"

        msg = "<soapenv:Envelope xmlns:soapenv='http://schemas."
        msg += "xmlsoap.org/soap/envelope/' xmlns:urn='urn:services-progress"
        msg += "-com:cttox:gebven001w:gebven001w'>"
        msg += "<soapenv:Header/>"
        msg += "<soapenv:Body>"
        msg += "<urn:Connect_gebven001w>"
        msg += "<urn:userId>supervisor</urn:userId>"
        msg += "<urn:password>gierp</urn:password>"
        msg += "<urn:appServerInfo>?</urn:appServerInfo>"
        msg += "</urn:Connect_gebven001w>"
        msg += "</soapenv:Body>"
        msg += "</soapenv:Envelope>"

        headers = {
            'content-type': "text/xml",
            'soapaction': "Connect_gebven001w",
        }

        try:
            response = requests.request(
                "POST",
                url,
                data=msg,
                headers=headers
            )

            # print(response.text)

            resultados_mensaje = response.content
            dom = parseString(resultados_mensaje)
            nodo = dom.getElementsByTagName('UUID')
            token = nodo[0].firstChild.nodeValue

            # print(token)
            # print(serialized)
        except Exception as e:
            error = tools.ustr(traceback.format_exc())
            # # print error
            raise ValidationError('Ocurrio un error al firmarse en \
                                  Progress favor de notificar al \
                                  Administrador del sistema')

        msgrel = "<soapenv:Envelope xmlns:soapenv='http://schemas."
        msgrel += "xmlsoap.org/soap/envelope/' xmlns:urn='urn:services-progres"
        msgrel += "s-com:cttox:gebven001w:gebven001w'>"
        msgrel += "<soapenv:Header>"
        msgrel += "<urn:gebven001wID>"
        msgrel += "<urn:UUID>" + token + "</urn:UUID>"
        msgrel += "</urn:gebven001wID>"
        msgrel += "</soapenv:Header>"
        msgrel += "<soapenv:Body>"
        msgrel += "<urn:Release_gebven001w/>"
        msgrel += "</soapenv:Body>"
        msgrel += "</soapenv:Envelope>"

        headrel = {
            'content-type': "text/xml",
            'soapaction': "Release_gebven001w",
        }

        # ejecuta query
        headers = {
            'content-type': "text/xml",
            'soapaction': "gebven001w",
        }

        msg = "<soapenv:Envelope xmlns:soapenv='http://schemas."
        msg += "xmlsoap.org/soap/envelope/' xmlns:urn='urn:services-progress"
        msg += "-com:cttox:gebven001w:gebven001w'>>"
        msg += "<soapenv:Header>"
        msg += "<urn:gebven001wID>"
        msg += "<urn:UUID><![CDATA[" + token + "]]></urn:UUID>"
        msg += "</urn:gebven001wID>"
        msg += "</soapenv:Header>"
        msg += "<soapenv:Body>"
        msg += "<urn:gebven001w>"
        msg += "<urn:mPVN_FOLIO>" + folio + "</urn:mPVN_FOLIO>"
        msg += "<urn:mCONCATENADO>" + serializado + "</urn:mCONCATENADO>"
        msg += "<urn:mCREACANCELA>" + str(creacancela) + "</urn:mCREACANCELA>"
        msg += "</urn:gebven001w>"
        msg += "</soapenv:Body>"
        msg += "</soapenv:Envelope>"

        try:
            response = requests.request(
                "POST",
                url,
                data=msg,
                headers=headers
            )

            # print(response.text)
            resultados_mensaje = response.content
            dom = parseString(resultados_mensaje)
            nodo = dom.getElementsByTagName('mERROR')
            res = nodo[0].firstChild.nodeValue
            mensaje = res.split('|')
        except Exception as e:
            response = requests.request(
                "POST",
                url,
                data=msgrel,
                headers=headrel
            )
            error = tools.ustr(traceback.format_exc())
            # # print error
            raise ValidationError('Ocurrio un error al enviar Información \
                                  a Progress favor de notificar \
                                  al Administrador del sistema')

        response = requests.request(
            "POST",
            url,
            data=msgrel,
            headers=headrel
        )

        if mensaje[0] == 'ERROR':
            raise ValidationError('Ocurrio un error del lado de OpenEdge \
                                  OpenEdge dice: ' + mensaje[1])

        mensaje.pop(0)
        return mensaje
