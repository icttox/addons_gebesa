# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
import requests
import traceback
import unicodedata
from xml.dom.minidom import parseString


class MrpShipment(models.Model):
    _inherit = 'mrp.shipment'

    @api.multi
    def done(self):
        encabezado, detalle = super().done()

        encabezado = unicodedata.normalize('NFD', encabezado).encode(
            'ascii', 'ignore')
        detalle = unicodedata.normalize('NFD', detalle).encode(
            'ascii', 'ignore')

        url = "http://148.244.148.218:8060/wsa/wsa1"

        msg = "<soapenv:Envelope xmlns:soapenv='http://schemas."
        msg += "xmlsoap.org/soap/envelope/' xmlns:urn='urn:services-progress"
        msg += "-com:cesar:wsaemb001w:wsaemb001w'>"
        msg += "<soapenv:Header/>"
        msg += "<soapenv:Body>"
        msg += "<urn:Connect_wsaemb001w>"
        msg += "<urn:userId>supervisor</urn:userId>"
        msg += "<urn:password>gierp</urn:password>"
        msg += "<urn:appServerInfo>?</urn:appServerInfo>"
        msg += "</urn:Connect_wsaemb001w>"
        msg += "</soapenv:Body>"
        msg += "</soapenv:Envelope>"

        headers = {
            'content-type': "text/xml",
            'soapaction': "Connect_wsaemb001w",
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
            # print error
            raise ValidationError('Ocurrio un error al firmarse en \
                                  Progress favor de notificar al \
                                  Administrador del sistema')

        msgrel = "<soapenv:Envelope xmlns:soapenv='http://schemas."
        msgrel += "xmlsoap.org/soap/envelope/' xmlns:urn='urn:services-progres"
        msgrel += "s-com:cesar:wsaemb001w:wsaemb001w'>"
        msgrel += "<soapenv:Header>"
        msgrel += "<urn:wsaemb001wID>"
        msgrel += "<urn:UUID>" + token + "</urn:UUID>"
        msgrel += "</urn:wsaemb001wID>"
        msgrel += "</soapenv:Header>"
        msgrel += "<soapenv:Body>"
        msgrel += "<urn:Release_wsaemb001w/>"
        msgrel += "</soapenv:Body>"
        msgrel += "</soapenv:Envelope>"

        headrel = {
            'content-type': "text/xml",
            'soapaction': "Release_wsaemb001w",
        }

        # ejecuta query
        headers = {
            'content-type': "text/xml",
            'soapaction': "wsaemb001w",
        }

        msg = "<soapenv:Envelope xmlns:soapenv='http://schemas."
        msg += "xmlsoap.org/soap/envelope/' xmlns:urn='urn:services-progres"
        msg += "s-com:cesar:wsaemb001w:wsaemb001w'>"
        msg += "<soapenv:Header>"
        msg += "<urn:wsaemb001wID>"
        msg += "<urn:UUID><![CDATA[" + token + "]]></urn:UUID>"
        msg += "</urn:wsaemb001wID>"
        msg += "</soapenv:Header>"
        msg += "<soapenv:Body>"
        msg += "<urn:wsaemb001w>"
        msg += "<urn:gcENCABEZADO>" + encabezado + "</urn:gcENCABEZADO>"
        msg += "<urn:gcDETALLE>" + detalle + "</urn:gcDETALLE>"
        msg += "</urn:wsaemb001w>"
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
            nodo = dom.getElementsByTagName('gcRESPONSE')
            res = nodo[0].firstChild.nodeValue
            mensaje = res.split('|')
        except Exception, e:
            response = requests.request(
                "POST",
                url,
                data=msgrel,
                headers=headrel
            )
            error = tools.ustr(traceback.format_exc())
            # print error
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
