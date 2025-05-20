# -*- coding: utf-8 -*-
# © 2019 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# import base64
from xml.dom.minidom import parseString
import traceback
from odoo import fields, api, models, tools
from odoo.exceptions import ValidationError
# from odoo.addons.immex_gebesa.models import util
# from odoo.addons.immex_gebesa.models.settings import PATH
import requests
# from tempfile import TemporaryFile
# import os

# PEM_F = os.path.join(PATH['PEM'])
# CER_F = os.path.join(PATH['CER'])
CONSULTA_PEDIMENTO = 'immex_gebesa.consultar_pedimento_vucem'
CONSULTA_PARTIDA = 'immex_gebesa.consultar_partida_vucem'


class WsGetPedimento(models.TransientModel):
    _name = 'ws.get.pedimento'
    _description = 'descripcion pendiente'

    aduana = fields.Integer(
        string='Aduana',
        help="Aduana E/S",
        required=True,
    )

    patente = fields.Integer(
        string='Patente',
        help="Numero de patente adduanal",
        required=True,
    )

    pedimento = fields.Integer(
        string='Pedimento',
        help="Numero de pedimento a 7 digitios",
        required=True,
    )

    @api.multi
    def get_pedimento(self):
        pedimento = self.env['l10n.mx.immex.pedimento'].search([
            ('num_pedimento', '=', str(self.pedimento).zfill(7))])
        if pedimento:
            raise ValidationError('Pedimento ya importado')

        values = {
            'user_name': self.env.user.company_id.partner_id.vat,
            'user_pass': self.env.user.company_id.pass_vucem,
            'clave_aduana': str(self.aduana),
            'patente': str(self.patente),
            'num_pedimento': str(self.pedimento)
        }
        msg = self.env['ir.qweb'].render(CONSULTA_PEDIMENTO, values=values)

        try:
            responsep = requests.request(
                "POST",
                'https://www.ventanillaunica.gob.mx/ventanilla-ws-pedimentos/ConsultarPedimentoCompletoService',
                data=msg,
                headers={
                    'content-type': 'text/xml; charset=utf-8',
                }
            )

            dom = parseString(responsep.content)

            numero_operacion = dom.getElementsByTagName(
                'ns2:numeroOperacion')[0].firstChild.nodeValue or False

            encabezado = dom.getElementsByTagName(
                'ns2:encabezado')[0] or False

            impoexpo = dom.getElementsByTagName(
                'ns2:importadorExportador')[0] or False

            # tasas = dom.getElementsByTagName(
            #     'ns2:tasas')[0].firstChild.nodeValue or False

            # provcomp = dom.getElementsByTagName(
            #     'ns2:proveedoresCompradores')[0].firstChild.nodeValue or False

            # facturas = dom.getElementsByTagName(
            #     'ns2:facturas')[0].firstChild.nodeValue or False

            # transportes = dom.getElementsByTagName(
            #     'ns2:transportes')[0].firstChild.nodeValue or False

            # guias = dom.getElementsByTagName(
            #     'ns2:guias')[0].firstChild.nodeValue or False

            # identificadores = dom.getElementsByTagName(
            #     'ns2:identificadores')[0].firstChild.nodeValue or False

            # observaciones = dom.getElementsByTagName(
            #     'ns2:observaciones')[0].firstChild.nodeValue or False

            pedimento_num = self.procesa_encabezado(encabezado, impoexpo)

            partidas = dom.getElementsByTagName('ns2:partidas')

            clave_documento = encabezado.getElementsByTagName(
                'ns2:claveDocumento')[0].firstChild.nodeValue or False

            for partida in partidas:
                numpar = partida.firstChild.nodeValue

                values['numero_operacion'] = numero_operacion
                values['numero_partida'] = numpar
                msg2 = self.env['ir.qweb'].render(CONSULTA_PARTIDA, values=values)

                try:
                    responsli = requests.request(
                        "POST",
                        'https://www.ventanillaunica.gob.mx/ventanilla-ws-pedimentos/ConsultarPartidaService',
                        data=msg2,
                        headers={
                            'content-type': 'text/xml; charset=utf-8',
                        }
                    )
                    resultparti = responsli.content
                    dom2 = parseString(resultparti)

                    partida = dom2.getElementsByTagName(
                        'ns9:partida')[0] or False
                    self.procesa_partida(partida, clave_documento, numpar, pedimento_num)
                except Exception as err:
                    error = tools.ustr(traceback.format_exc())
                    if hasattr(error, 'name'):
                        error = err.name
                    elif hasattr(error, 'message'):
                        error = err.message
                    raise ValidationError(('Ocurrio un error al consultar la partida en \
                                          el sitio del VUCEM favor de notificar al \
                                          Administrador del sistema %s') % error)
        except Exception as err:
            error = tools.ustr(traceback.format_exc())
            if hasattr(error, 'name'):
                error = err.name
            elif hasattr(error, 'message'):
                error = err.message
            raise ValidationError(('Ocurrio un error al consultar el pedimento en \
                                  el sitio del VUCEM favor de notificar al \
                                  Administrador del sistema %s') % error)

    def procesa_encabezado(self, encabezado, impoexpo):

        tipo_operacion = encabezado.getElementsByTagName(
            'ns2:tipoOperacion')[0] or False
        # <ns2:clave>

        clave_documento = encabezado.getElementsByTagName(
            'ns2:claveDocumento')[0] or False
        # <ns2:clave>

        destino = encabezado.getElementsByTagName(
            'ns2:destino')[0] or False
        # <ns2:clave>

        aduana_entrada_salida = encabezado.getElementsByTagName(
            'ns2:aduanaEntradaSalida')[0] or False
        # <ns2:clave>

        tipo_cambio = encabezado.getElementsByTagName(
            'ns2:tipoCambio')[0].firstChild.nodeValue or False

        peso_bruto = encabezado.getElementsByTagName(
            'ns2:pesoBruto')[0].firstChild.nodeValue or False

        medio_trasnporte_salida = encabezado.getElementsByTagName(
            'ns2:medioTrasnporteSalida')[0] or False
        # <ns2:clave>

        medio_trasnporte_arribo = encabezado.getElementsByTagName(
            'ns2:medioTrasnporteArribo')[0] or False
        # <ns2:clave>

        medio_trasnporte_entrada = encabezado.getElementsByTagName(
            'ns2:medioTrasnporteEntrada')[0] or False
        # <ns2:clave>

        curp_apoderadomandatario = encabezado.getElementsByTagName(
            'ns2:curpApoderadomandatario')[0].firstChild.nodeValue or False

        # rfcAgenteAduanalSocFactura = encabezado.getElementsByTagName(
        #     'ns2:rfcAgenteAduanalSocFactura')[0].firstChild.nodeValue or False

        # valorDolares = False
        # if encabezado.getElementsByTagName('ns2:valorDolares'):
        #     valorDolares = encabezado.getElementsByTagName(
        #         'ns2:valorDolares')[0].firstChild.nodeValue or False

        # valorAduanalTotal = encabezado.getElementsByTagName(
        #     'ns2:valorAduanalTotal')[0].firstChild.nodeValue or False

        # valorComercialTotal = encabezado.getElementsByTagName(
        #     'ns2:valorComercialTotal')[0].firstChild.nodeValue or False

        # ImpoExpo ########################
        rfc = impoexpo.getElementsByTagName(
            'ns2:rfc')[0].firstChild.nodeValue or False

        razon_social = impoexpo.getElementsByTagName(
            'ns2:razonSocial')[0].firstChild.nodeValue or False

        domicilio = impoexpo.getElementsByTagName(
            'ns2:domicilio')[0] or False

        seguros = impoexpo.getElementsByTagName(
            'ns2:seguros')[0].firstChild.nodeValue or False

        fletes = impoexpo.getElementsByTagName(
            'ns2:fletes')[0].firstChild.nodeValue or False

        embalajes = impoexpo.getElementsByTagName(
            'ns2:embalajes')[0].firstChild.nodeValue or False

        incrementables = impoexpo.getElementsByTagName(
            'ns2:incrementables')[0].firstChild.nodeValue or False

        # aaduanaDespacho = impoexpo.getElementsByTagName(
        #     'ns2:aaduanaDespacho')[0] or False

        # bultos = impoexpo.getElementsByTagName(
        #     'ns2:bultos')[0].firstChild.nodeValue or False

        fechas = impoexpo.getElementsByTagName(
            'ns2:fechas') or False

        fechaent = ''
        fechapag = ''
        for fecha in fechas:
            valor = fecha.getElementsByTagName(
                'ns2:fecha')[0].firstChild.nodeValue or False
            tipo = fecha.getElementsByTagName(
                'ns2:tipo')[0] or False
            cvefec = tipo.getElementsByTagName(
                'ns2:clave')[0].firstChild.nodeValue or False
            valor_format = valor[:10] + ' ' + valor[11:]
            if cvefec == '1':
                fechaent = valor_format
            elif cvefec == '2':
                fechapag = valor_format
            # FECHAS ################################################
            # self.env['l10n.mx.immex.pedimento.fechas'].create({
            #     'patente': self.patente,
            #     'num_pedimento': self.pedimento,
            #     'clave_aduana': self.aduana,
            #     'tipo_fecha': cvefec,
            #     'fecha_operacion': valor,
            #     'fecha_validacion_pago': fechapag,
            #     'resumen_id': False,
            # })

        # efectivo = impoexpo.getElementsByTagName(
        #     'ns2:efectivo')[0].firstChild.nodeValue or False

        # otros = impoexpo.getElementsByTagName(
        #     'ns2:otros')[0].firstChild.nodeValue or False

        # total = impoexpo.getElementsByTagName(
        #     'ns2:total')[0].firstChild.nodeValue or False

        pais = impoexpo.getElementsByTagName(
            'ns2:pais')[0] or False

        # PEDIMENTO ###########################################################
        pedimento_num = (fechaent[2:4] + str(self.aduana)[:2] + '\
            ' + str(self.patente) + str(self.pedimento).zfill(7))

        self.env['l10n.mx.immex.pedimento'].create({
            'patente': str(self.patente),
            'num_pedimento': str(self.pedimento).zfill(7),
            'clave_aduana': str(self.aduana),
            'tipo_operacion': tipo_operacion.getElementsByTagName(
                'ns2:clave')[0].firstChild.nodeValue or False,
            'clave_documento': clave_documento.getElementsByTagName(
                'ns2:clave')[0].firstChild.nodeValue or False,
            'clave_seccion_aduanera': aduana_entrada_salida.getElementsByTagName(
                'ns2:clave')[0].firstChild.nodeValue or False,
            'curp_contribuyente': '',
            'rfc_contribuyente': rfc,
            'curp_agente': curp_apoderadomandatario,
            'tipo_cambio': tipo_cambio,
            'total_flete': fletes,
            'total_seguros': seguros,
            'total_embalages': embalajes,
            'total_otros_inc': incrementables,
            'total_otros_ded': '',
            'peso': peso_bruto,
            'output_medio_transporte': medio_trasnporte_salida.getElementsByTagName(
                'ns2:clave')[0].firstChild.nodeValue or False,
            'input_medio_transporte': medio_trasnporte_entrada.getElementsByTagName(
                'ns2:clave')[0].firstChild.nodeValue or False,
            'medio_transporte': medio_trasnporte_arribo.getElementsByTagName(
                'ns2:clave')[0].firstChild.nodeValue or False,
            'clave_destino': destino.getElementsByTagName(
                'ns2:clave')[0].firstChild.nodeValue or False,
            'nombre_contribuyente': razon_social,
            'calle_contribuyente': domicilio.getElementsByTagName(
                'ns2:calle')[0].firstChild.nodeValue or False,
            'num_interior_contribuyente': '',
            'num_exterior_contribuyente': domicilio.getElementsByTagName(
                'ns2:numeroExterior')[0].firstChild.nodeValue or False,
            'cp': domicilio.getElementsByTagName(
                'ns2:codigoPostal')[0].firstChild.nodeValue or False,
            'ciudad': domicilio.getElementsByTagName(
                'ns2:ciudadMunicipio')[0].firstChild.nodeValue or False,
            'estado': '',
            'pais': pais.getElementsByTagName(
                'clave')[0].firstChild.nodeValue or False,
            'tipo_pedimento': '',
            'fecha_pedimento': fechaent,
            'fecha_pago_real': fechapag,
            'resumen_id': False,
            'pedimento_num': pedimento_num
        })

        return pedimento_num

        # TRANSPORTES ###########################################################
        # for transportista in transportes:
        #     identificador = transportista.getElementsByTagName(
        #         'ns2:identificador').firstChild.nodeValue or False
        #     paisTransporte = transportista.getElementsByTagName(
        #         'ns2:paisTransporte').firstChild.nodeValue or False
        #     nombret = transportista.getElementsByTagName(
        #         'ns2:nombre').firstChild.nodeValue or False

        #     self.env['l10n.mx.immex.pedimento.transporte'].create({
        #         'patente': self.patente,
        #         'num_pedimento': self.pedimento,
        #         'clave_aduana': self.aduana,
        #         'rfc_transportirsta': '',
        #         'curp_transportista': '',
        #         'nombre_transportista': nombret,
        #         'pais_transportista': paisTransporte.getElementsByTagName(
        #             'ns2:clave')[0].firstChild.nodeValue or False,
        #         'id_transporte': identificador,
        #         'fecha_pago_transport': '',
        #         'resumen_id': False,
        #     })

        # GUIAS ###########################################################
        # for guia in guias:
        #     guiaManifiesto = guia.getElementsByTagName(
        #         'ns2:guiaManifiesto').firstChild.nodeValue or False

        #     tipoGuia = guia.getElementsByTagName(
        #         'ns2:tipoGuia').firstChild.nodeValue or False

        #     self.env['l10n.mx.immex.pedimento.guia'].create({
        #         'patente': self.patente,
        #         'num_pedimento': self.pedimento,
        #         'clave_aduana': self.aduana,
        #         'numero_guia': guiaManifiesto,
        #         'tipo_guia': tipoGuia,
        #         'fecha_pago_guia': '',
        #         'resumen_id': False,
        #     })

        # FACTURAS ###########################################################
        # url3 = 'https://www.ventanillaunica.gob.mx/ventanilla/ConsultarEdocumentService'
        # company_id = self.env.user.company_id

        # fiel = self.env['cfdi.fiel'].search([
        #     ('company_id', '=', company_id.id),
        #     ('active', '=', True)], order='id',
        #     limit=1)
        # fiel_file_pem = fiel.fiel_file_pem
        # certificado = base64.decodestring(fiel_file_pem)
        # certificado = certificado.replace('-----BEGIN CERTIFICATE-----', '')
        # certificado = certificado.replace('-----END CERTIFICATE-----', '')
        # certificado = certificado.replace('\n', '')

        # rfccomp = company_id.partner_id.vat[2:]
        # pass_vucem = company_id.pass_vucem
        # for factura in facturas:
        #     numerofac = factura.getElementsByTagName(
        #         'ns2:numero').firstChild.nodeValue or False

        #     fechafac = factura.getElementsByTagName(
        #         'ns2:fecha').firstChild.nodeValue or False

        #     terminoFacturacion = factura.getElementsByTagName(
        #         'ns2:terminoFacturacion').firstChild.nodeValue or False

        #     valorDolares = factura.getElementsByTagName(
        #         'ns2:valorDolares').firstChild.nodeValue or False

        #     valorMonedaExtranjera = factura.getElementsByTagName(
        #         'ns2:valorMonedaExtranjera').firstChild.nodeValue or False

        #     identificadorFiscalProveedorComprador = factura.getElementsByTagName(
        #         'ns2:identificadorFiscalProveedorComprador').firstChild.nodeValue or False

        #     proveedorComprador = factura.getElementsByTagName(
        #         'ns2:proveedorComprador').firstChild.nodeValue or False

        #     pedimento_factura = self.env[
        #         'l10n.mx.immex.pedimento.factura'].create({
        #             'patente': self.patente,
        #             'num_pedimento': self.pedimento,
        #             'clave_aduana': self.aduana,
        #             'fecha_facturacion': fechafac,
        #             'num_factura': numerofac,
        #             'termino_facturacion': terminoFacturacion.getElementsByTagName(
        #                 'ns2:clave')[0].firstChild.nodeValue or False,
        #             'moneda_factura': '',
        #             'monto_usd': valorDolares,
        #             'monto_extranjera': valorMonedaExtranjera,
        #             'pais_facturacion': '',
        #             'estado': '',
        #             'id_fiscal_proveedor': identificadorFiscalProveedorComprador,
        #             'nombre_proveedor': proveedorComprador,
        #             'calle_proveedor': '',
        #             'num_interior_proveedor': '',
        #             'num_exterior_proveedor': '',
        #             'cp_proveedor': '',
        #             'ciudad_proveedor': '',
        #             'fecha_real_pago': '',
        #             'resumen_id': False,
        #         })

        #     if 'COVE' in numerofac:
        #         cove = numerofac
        #         cadena_ori = '|' + rfc + '|' + cove + '|'
        #         self.do_tmpfiles(fiel)
        #         cadena_fir = util.get_sello_cadena_sha256(
        #             PEM_F, cadena_ori)

        #         msg3 = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" '
        #         msg3 += 'xmlns:con="http://www.ventanillaunica.gob.mx/ConsultarEdocument/" '
        #         msg3 += 'xmlns:oxml="http://www.ventanillaunica.gob.mx/cove/ws/oxml/">'
        #         msg3 += '<soapenv:Header>'
        #         msg3 += '<wsse:Security soapenv:mustUnderstand="1" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">'
        #         msg3 += '<wsse:UsernameToken>'
        #         msg3 += '<wsse:Username>'
        #         msg3 += rfccomp
        #         msg3 += '</wsse:Username>'
        #         msg3 += '<wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">'
        #         msg3 += pass_vucem
        #         msg3 += '</wsse:Password>'
        #         msg3 += '</wsse:UsernameToken>'
        #         msg3 += '</wsse:Security>'
        #         msg3 += '</soapenv:Header>'
        #         msg3 += '<soapenv:Body>'
        #         msg3 += '<con:ConsultarEdocumentRequest>'
        #         msg3 += '<con:request>'
        #         msg3 += '<con:firmaElectronica>'
        #         msg3 += '<oxml:certificado><![CDATA['
        #         msg3 += certificado
        #         msg3 += ']]></oxml:certificado>'
        #         msg3 += '<oxml:cadenaOriginal>'
        #         msg3 += cadena_ori
        #         msg3 += '</oxml:cadenaOriginal>'
        #         msg3 += '<oxml:firma><![CDATA['
        #         msg3 += cadena_fir
        #         msg3 += ']]></oxml:firma>'
        #         msg3 += '</con:firmaElectronica>'
        #         msg3 += '<con:criterioBusqueda>'
        #         msg3 += '<con:eDocument>'
        #         msg3 += cove
        #         msg3 += '</con:eDocument>'
        #         msg3 += '<con:numeroAdenda></con:numeroAdenda>'
        #         msg3 += '</con:criterioBusqueda>'
        #         msg3 += '</con:request>'
        #         msg3 += '</con:ConsultarEdocumentRequest>'
        #         msg3 += '</soapenv:Body>'
        #         msg3 += '</soapenv:Envelope>'
        #         pedimento_factura.requests = msg3
        #         headers = {
        #             'content-type': 'text/xml; charset=utf-8',
        #         }
        #         try:
        #             response = requests.request(
        #                 "POST",
        #                 url3,
        #                 data=msg3,
        #                 headers=headers
        #             )
        #             resultados_mensaje = response.content
        #             pedimento_factura.response = resultados_mensaje
        #             dom = parseString(resultados_mensaje)
        #             numero_factura = dom.getElementsByTagName(
        #                 'numeroFacturaRelacionFacturas')[0].firstChild.nodeValue or False
        #             if numero_factura:
        #                 invoice = self.env['account.invoice'].search([(
        #                     'reference', '=', numero_factura)])
        #                 if invoice:
        #                     self._cr.execute("""
        #                         UPDATE account_invoice set
        #                             patente_aduanal = %s,
        #                             petition_number = %s,
        #                             clave_aduanal = %s,
        #                             cove = %s
        #                         WHERE id = %s""", (
        #                         self.patente, self.pedimento, self.aduana, numerofac,
        #                         invoice.id))
        #                     pedimento_factura.invoice_id = invoice.id
        #                 else:
        #                     invoice = self.env['account.invoice'].search(['|', (
        #                         'number', '=', numero_factura), (
        #                         'cfdi_uuid', '=', numero_factura)])
        #                     if invoice:
        #                         self._cr.execute("""
        #                             UPDATE account_invoice set
        #                                 patente_aduanal = %s,
        #                                 petition_number = %s,
        #                                 clave_aduanal = %s,
        #                                 cove = %s
        #                             WHERE id = %s""", (
        #                             self.patente, self.pedimento, self.aduana, numerofac,
        #                             invoice.id))
        #                         pedimento_factura.invoice_id = invoice.id
        #         except Exception, e:
        #             continue
        #     else:
        #         invoice = self.env['account.invoice'].search([(
        #             'cfdi_uuid', '=', numerofac)])
        #         if invoice:
        #             self._cr.execute("""
        #                 UPDATE account_invoice set
        #                     patente_aduanal = %s,
        #                     petition_number = %s,
        #                     clave_aduanal = %s
        #                 WHERE id = %s""", (
        #                 self.patente, self.pedimento, self.aduana, numerofac, invoice.id))
        #             pedimento_factura.invoice_id = invoice.id

        # TASAS ###########################################################
        # for tasa in tasas:
        #     contribucion = tasa.getElementsByTagName(
        #         'ns2:contribucion').firstChild.nodeValue or False
        #     tipotasa = tasa.getElementsByTagName(
        #         'ns2:tipoTasa').firstChild.nodeValue or False
        #     tasaapli = tasa.getElementsByTagName(
        #         'ns2:tasaAplicable').firstChild.nodeValue or False
        #     formapago = tasa.getElementsByTagName(
        #         'ns2:formaPago').firstChild.nodeValue or False
        #     importecont = tasa.getElementsByTagName(
        #         'ns2:importe').firstChild.nodeValue or False

        #     self.env['l10n.mx.immex.pedimento.tasas'].create({
        #         'patente': self.patente,
        #         'num_pedimento': self.pedimento,
        #         'clave_aduana': self.aduana,
        #         'clave_contribucion': contribucion.getElementsByTagName(
        #             'ns2:clave')[0].firstChild.nodeValue or False,
        #         'tasa': tasaapli,
        #         'tipo_tasa': tipotasa.getElementsByTagName(
        #             'ns2:clave')[0].firstChild.nodeValue or False,
        #         'tipo_pedimento': '',
        #         'fecha_pago_real': '',
        #         'resumen_id': False,
        #     })
        #     # CONTRIBUCIONES ####################################################
        #     self.env['l10n.mx.immex.pedimento.contribuciones'].create({
        #         'patente': self.patente,
        #         'num_pedimento': self.pedimento,
        #         'clave_aduana': self.aduana,
        #         'clave_contribucion': contribucion.getElementsByTagName(
        #             'ns2:clave')[0].firstChild.nodeValue or False,
        #         'forma_pago': formapago.getElementsByTagName(
        #             'ns2:clave')[0].firstChild.nodeValue or False,
        #         'importe': importecont,
        #         'tipo_pedimento': '',
        #         'fecha_pago_real': '',
        #         'resumen_id': False,
        #     })

        # mi = 1
        # for observacion in observaciones:
        #     nota = tasa.getElementsByTagName(
        #         'ns2:observaciones').firstChild.nodeValue or False
        #     self.env['l10n.mx.immex.pedimento.observaciones'].create({
        #         'patente': self.patente,
        #         'num_pedimento': self.pedimento,
        #         'clave_aduana': self.aduana,
        #         'secuencia': str(mi),
        #         'observaciones': nota,
        #         'tipo_pedimento': '',
        #         'fecha_pago_real': '',
        #         'resumen_id': False,
        #     })
        #     mi += 1

    @api.multi
    def procesa_partida(self, partida, clavedocto, numpar, pedimento_num):
        fraccion = partida.getElementsByTagName(
            'ns8:fraccionArancelaria')[0].firstChild.nodeValue or False
        descmcia = partida.getElementsByTagName(
            'ns8:descripcionMercancia')[0].firstChild.nodeValue or False

        umt = partida.getElementsByTagName(
            'ns8:unidadMedidaTarifa')[0] or False
        qtyumt = partida.getElementsByTagName(
            'ns8:cantidadUnidadMedidaTarifa')[0].firstChild.nodeValue or False
        umc = partida.getElementsByTagName(
            'ns8:unidadMedidaComercial')[0] or False
        qtyumc = partida.getElementsByTagName(
            'ns8:cantidadUnidadMedidaComercial')[0].firstChild.nodeValue or False
        preuni = partida.getElementsByTagName(
            'ns8:precioUnitario')[0].firstChild.nodeValue or False
        valcom = partida.getElementsByTagName(
            'ns8:valorComercial')[0].firstChild.nodeValue or False
        valadu = partida.getElementsByTagName(
            'ns8:valorAduana')[0].firstChild.nodeValue or False
        valusd = partida.getElementsByTagName(
            'ns8:valorDolares')[0].firstChild.nodeValue or False
        valagr = partida.getElementsByTagName(
            'ns8:valorAgregado')[0].firstChild.nodeValue or False

        metvalor = partida.getElementsByTagName(
            'ns8:metodoValoracion')[0].firstChild.nodeValue or False
        vincula = partida.getElementsByTagName(
            'ns8:vinculacion')[0].firstChild.nodeValue or False
        paisoridest = partida.getElementsByTagName(
            'ns8:paisOrigenDestino')[0] or False
        paisvencompra = partida.getElementsByTagName(
            'ns8:paisVendedorComprador')[0] or False
        # try:
        #     observaciones = partida.getElementsByTagName(
        #         'ns8:observaciones')[0].firstChild.nodeValue or False
        # except Exception as err:
        #     observaciones = ''

        # gravamenes = partida.getElementsByTagName(
        #     'ns8:gravamenes')[0] or False

        self.env['l10n.mx.immex.partida'].create({
            'patente': self.patente,
            'num_pedimento': str(self.pedimento).zfill(7),
            'clave_aduana': self.aduana,
            'fraccion_arancelaria': fraccion,
            'secuencia_fraccion': numpar,
            'subdivision_fraccion': '',
            'descripcion': descmcia,
            'precio_unitario': preuni,
            'valor_aduana': valadu,
            'valor_comercial': valcom,
            'valor_usd': valusd,
            'cantidad_udm_comercial': qtyumc,
            'udm_comercial': umc.getElementsByTagName(
                'ns8:clave')[0].firstChild.nodeValue or False,
            'cantidad_udm_tarifa': qtyumt,
            'udm_tarifa': umt.getElementsByTagName(
                'ns8:clave')[0].firstChild.nodeValue or False,
            'valor_agregado': valagr,
            'clave_vinculacion': vincula,
            'metodo_valorizacion': metvalor,
            'codigo_mercancia': '',
            'marca_mercancia': '',
            'modelo_mercancia': '',
            'pais': paisoridest.getElementsByTagName(
                'ns8:clave')[0].firstChild.nodeValue or False,
            'pais_extranjero': paisvencompra.getElementsByTagName(
                'ns8:clave')[0].firstChild.nodeValue or False,
            'estado_origen': '',
            'estado_destino': '',
            'estado_comprador': '',
            'estado_vendedor': '',
            'tipo_operacion': '',
            'clave_documento': clavedocto,
            'fecha_pago_real': False,
            'resumen_id': False,
            'amount': qtyumc,
            'pedimento_num': pedimento_num,
        })

    # @api.multi
    # def do_tmpfiles(self, fiel_id):
    #     """ Write tmp Cer file
    #     """
    #     for imp in self:
    #         if not fiel_id:
    #             raise exceptions.ValidationError(
    #                 "There is not a valid Certificate (CSD)"
    #                 "for the company emmiter of this invoice,"
    #                 " verify please...")

    #         pem_file = fiel_id.fiel_key_file_pem

    #         with open(PEM_F, 'wb') as f:
    #             f.write(base64.decodestring(pem_file or ''))
    #             f.close()

    #         cer_file = fiel_id.fiel_file

    #         with open(CER_F, 'wb') as f:
    #             f.write(base64.decodestring(cer_file or ''))
    #             f.close()
