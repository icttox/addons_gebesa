# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import traceback
from xml.dom.minidom import parseString
import logging
from odoo import _, api, exceptions, fields, models, tools
import requests

CONSULTA_PEDIMENTO = 'immex_gebesa.consultar_pedimento_vucem'
DESCARGAR_EDOCUMENT = 'immex_gebesa.descargar_edocument_vucem'
DESCARGAR_ACUSE = 'immex_gebesa.descargar_acuse_vucem'

DATOS_COVE = {
    'tipoOperacion': {
        'TOCE.IMP': 'Importación',
        'TOCE.EXP': 'Exportación'
    },
    'tipoFigura': {
        '1': 'Agente Aduanal',
        '2': 'Apoderado Aduanal',
        '3': 'Mandatario',
        '4': 'Exportador',
        '5': 'Importador'
    },
    'relacionFacturas': {
        '0': 'No es Relación de CFDI o documentos equivalentes',
        '1': ' Es Relación del CFDI o documento equivalente'
    },
    'certificadoOrigen': {
        '0': ' No Funge como certificado de origen',
        '1': 'Si Funge como certificado de origen'
    },
    'subdivision': {
        '0': 'Sin subdivisión',
        '1': ' Con subdivisión'
    },
    'tipoIdentificador': {
        '0': 'Tax Id',
        '1': 'RFC',
        '2': 'CURP',
        '3': 'Sin Tax Id',
    }
}

_logger = logging.getLogger(__name__)


class L10nMxImmexPedimento(models.Model):
    _name = 'l10n.mx.immex.pedimento'
    _inherit = ['message.post.show.all']
    _rec_name = 'pedimento_num'

    patente = fields.Char(
        string='patente',
    )
    num_pedimento = fields.Char(
        string='Numero pedimento',
    )
    clave_aduana = fields.Char(
        string='Clave aduana',
    )
    tipo_operacion = fields.Char(
        string='Tipo de operación',
    )
    clave_documento = fields.Char(
        string='Clave del documento',
    )
    clave_seccion_aduanera = fields.Char(
        string='Clave seccion aduana',
    )
    curp_contribuyente = fields.Char(
        string='CURP del Importador / Exportador',
    )
    rfc_contribuyente = fields.Char(
        string='RFC del Importador / Exportador',
    )
    curp_agente = fields.Char(
        string='CURP del agente o apoderado',
    )
    tipo_cambio = fields.Char(
        string='Tipo de cambio',
    )
    total_flete = fields.Char(
        string='Total de fletes',
    )
    total_seguros = fields.Char(
        string='Total de seguros',
    )
    total_embalages = fields.Char(
        string='Total de embalajes',
    )
    total_otros_inc = fields.Char(
        string='Total de otros incrementables',
    )
    total_otros_ded = fields.Char(
        string='Total de otros deducibles',
    )
    peso = fields.Char(
        string='Peso bruto de la mercancía',
    )
    output_medio_transporte = fields.Char(
        string='Clave del medio de transporte de salida',
    )
    input_medio_transporte = fields.Char(
        string='Clave del medio de transporte de arrivo',
    )
    medio_transporte = fields.Char(
        string='Clave del medio de transporte de entrada o salida',
    )
    clave_destino = fields.Char(
        string='Clave de destino de la mercancía',
    )
    nombre_contribuyente = fields.Char(
        string='Razon Social del contribuyente',
    )
    calle_contribuyente = fields.Char(
        string='Calle del contribuyente',
    )
    num_interior_contribuyente = fields.Char(
        string='Numero interior contribuyente',
    )
    num_exterior_contribuyente = fields.Char(
        string='Numero exterior del contribuyente',
    )
    cp = fields.Char(
        string='Código postal del contribuyente',
    )
    ciudad = fields.Char(
        string='Municipio o ciudad del contribuyente',
    )
    estado = fields.Char(
        string='Clave de entidad federativa del contribuyente',
    )
    pais = fields.Char(
        string='Clave del pais del contribuyente',
    )
    tipo_pedimento = fields.Char(
        string='Clave del tipo de pedimento',
    )
    fecha_pedimento = fields.Datetime(
        string='Fecha de recepción del pedimento',
    )
    fecha_pago_real = fields.Datetime(
        string='Fecha de pago de las contribuciones y cuotas compensatorias',
    )
    resumen_id = fields.Many2one(
        'l10n.mx.immex.resumen',
        string='Resumen id',
    )
    pedimento_num = fields.Char(
        string='Pedimento Numero',
        compute='_compute_pedimento_num',
        store=True
    )
    regime_changed = fields.Boolean(
        string='Cambio de Régimen',
    )
    factura_ids = fields.One2many(
        'l10n.mx.immex.pedimento.factura',
        'pedimento_id',
        string='Factura'
    )
    partida_ids = fields.One2many(
        'l10n.mx.immex.partida',
        'pedimento_id',
        string='Partida'
    )
    rectificaciones_ids = fields.One2many(
        'l10n.mx.immex.pedimento.rectificaciones',
        'pedimento_id',
        string='Rectificaciones'
    )
    transporte_ids = fields.One2many(
        'l10n.mx.immex.pedimento.transporte',
        'pedimento_id',
        string='Transporte'
    )
    contenedor_ids = fields.One2many(
        'l10n.mx.immex.pedimento.contenedor',
        'pedimento_id',
        string='Contenedor'
    )
    fechas_ids = fields.One2many(
        'l10n.mx.immex.pedimento.fechas',
        'pedimento_id',
        string='Fechas'
    )
    casos_ids = fields.One2many(
        'l10n.mx.immex.pedimento.casos',
        'pedimento_id',
        string='Casos'
    )
    observaciones_ids = fields.One2many(
        'l10n.mx.immex.pedimento.observaciones',
        'pedimento_id',
        string='Observaciones'
    )
    guias_ids = fields.One2many(
        'l10n.mx.immex.pedimento.guia',
        'pedimento_id',
        string='Guias'
    )
    cuentas_ids = fields.One2many(
        'l10n.mx.immex.pedimento.cuentas',
        'pedimento_id',
        string='Cuentas'
    )
    tasas_ids = fields.One2many(
        'l10n.mx.immex.pedimento.tasas',
        'pedimento_id',
        string='Tasas'
    )
    contribuciones_ids = fields.One2many(
        'l10n.mx.immex.pedimento.contribuciones',
        'pedimento_id',
        string='Contribuciones'
    )
    descargos_ids = fields.One2many(
        'l10n.mx.immex.pedimento.descargos',
        'pedimento_id',
        string='Descargos'
    )
    destinatarios_ids = fields.One2many(
        'l10n.mx.immex.pedimento.destinatarios',
        'pedimento_id',
        string='Destinatarios'
    )
    diferencias_ids = fields.One2many(
        'l10n.mx.immex.pedimento.diferencias',
        'pedimento_id',
        string='Diferencias'
    )
    seleccion_ids = fields.One2many(
        'l10n.mx.immex.pedimento.seleccion',
        'pedimento_id',
        string='Selección'
    )
    documentos_digitalizados_ids = fields.One2many(
        'l10n.mx.immex.pedimento.documentos.digitalizados',
        'pedimento_id',
        string='Documentos digitalizados',
    )
    descargos_ids = fields.One2many(
        'l10n.mx.immex.pedimento.descargos',
        'pedimento_id',
        string='Descargos'
    )

    rectified_with_id = fields.Many2one(
        'l10n.mx.immex.pedimento',
        string='Rectificado con',
    )

    @api.multi
    @api.depends('clave_aduana', 'fecha_pedimento', 'num_pedimento', 'patente')
    def _compute_pedimento_num(self):
        for ped in self:
            fec_ped = ''
            cla_adu = ''
            if ped.fecha_pedimento:
                fec_ped = str(ped.fecha_pedimento)[2:4]
            if ped.clave_aduana:
                cla_adu = ped.clave_aduana[:2]
            ped.pedimento_num = (
                fec_ped + cla_adu + (
                    ped.patente or '') + (ped.num_pedimento or ''))

    def import_for_data_stage(self, lines, resumen):
        for line in lines:
            line = line.replace('\r\n', '')
            line = line.replace('\x00', '')
            line = line.split("|")

            pedimento = self.search([
                ('patente', '=', line[0]),
                ('num_pedimento', '=', line[1]),
                ('clave_aduana', '=', line[2])])

            if pedimento:
                pedimento.write({
                    'tipo_operacion': line[3],
                    'clave_documento': line[4],
                    'clave_seccion_aduanera': line[5],
                    'curp_contribuyente': line[6],
                    'rfc_contribuyente': line[7],
                    'curp_agente': line[8],
                    'tipo_cambio': line[9],
                    'total_flete': line[10],
                    'total_seguros': line[11],
                    'total_embalages': line[12],
                    'total_otros_inc': line[13],
                    'total_otros_ded': line[14],
                    'peso': line[15],
                    'output_medio_transporte': line[16],
                    'input_medio_transporte': line[17],
                    'medio_transporte': line[18],
                    'clave_destino': line[19],
                    'nombre_contribuyente': line[20],
                    'calle_contribuyente': line[21],
                    'num_interior_contribuyente': line[22],
                    'num_exterior_contribuyente': line[23],
                    'cp': line[24],
                    'ciudad': line[25],
                    'estado': line[26],
                    'pais': line[27],
                    'tipo_pedimento': line[28],
                    'fecha_pedimento': line[29],
                    'fecha_pago_real': line[30],
                    'resumen_id': resumen.id,
                })
            else:
                self.create({
                    'patente': line[0],
                    'num_pedimento': line[1],
                    'clave_aduana': line[2],
                    'tipo_operacion': line[3],
                    'clave_documento': line[4],
                    'clave_seccion_aduanera': line[5],
                    'curp_contribuyente': line[6],
                    'rfc_contribuyente': line[7],
                    'curp_agente': line[8],
                    'tipo_cambio': line[9],
                    'total_flete': line[10],
                    'total_seguros': line[11],
                    'total_embalages': line[12],
                    'total_otros_inc': line[13],
                    'total_otros_ded': line[14],
                    'peso': line[15],
                    'output_medio_transporte': line[16],
                    'input_medio_transporte': line[17],
                    'medio_transporte': line[18],
                    'clave_destino': line[19],
                    'nombre_contribuyente': line[20],
                    'calle_contribuyente': line[21],
                    'num_interior_contribuyente': line[22],
                    'num_exterior_contribuyente': line[23],
                    'cp': line[24],
                    'ciudad': line[25],
                    'estado': line[26],
                    'pais': line[27],
                    'tipo_pedimento': line[28],
                    'fecha_pedimento': line[29],
                    'fecha_pago_real': line[30],
                    'resumen_id': resumen.id,
                })

    def _descargar_expediente_digital(self):
        pedimentos = self.search([
            ('documentos_digitalizados_ids', '=', False),
            ('clave_documento', 'in', ['IN', 'V1', 'AF', 'RT'])
        ], limit=10)
        for pedimento in pedimentos:
            pedimento.descargar_expediente_digital()

    def descargar_expediente_digital(self):
        values = {
            'user_name': self.env.user.company_id.partner_id.vat,
            'user_pass': self.env.user.company_id.pass_vucem,
            'clave_aduana': self.clave_aduana,
            'patente': self.patente,
            'num_pedimento': self.num_pedimento
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
        except Exception as err:
            error = tools.ustr(traceback.format_exc())
            if hasattr(error, 'name'):
                error = err.name
            elif hasattr(error, 'message'):
                error = err.message
            raise exceptions.ValidationError((
                'Ocurrio un error al consultar el pedimento en \
                 el sitio del VUCEM favor de notificar al \
                 Administrador del sistema %s') % error)

        dom = parseString(responsep.content)

        if dom.getElementsByTagName('ns3:tieneError') and dom.getElementsByTagName(
                'ns3:tieneError')[0].firstChild.nodeValue != 'false':
            error = dom.getElementsByTagName('ns3:error')[0].getElementsByTagName(
                'ns3:mensaje')[0].firstChild.nodeValue or False
            raise exceptions.ValidationError((
                'El sitio del VUCEM regreso el siguiente error: \n %s') % error)

        if not dom.getElementsByTagName('ns2:identificadores'):
            error = dom.getElementsByTagName('faultstring')[0].firstChild.nodeValue
            raise exceptions.ValidationError((
                'El sitio del VUCEM regreso el siguiente error: \n %s') % error)

        identificadores = dom.getElementsByTagName(
            'ns2:identificadores')[0].getElementsByTagName(
            'ns2:identificadores')
        for identificador in identificadores:
            clave = identificador.getElementsByTagName(
                'claveIdentificador') or False
            if clave and ((clave[0].getElementsByTagName('clave')[
                    0].firstChild.nodeValue or False) == 'ED'):
                complemento = identificador.getElementsByTagName(
                    'complemento1')[0].firstChild.nodeValue or False
                doc_dig = self.env[
                    'l10n.mx.immex.pedimento.documentos.digitalizados'].search([
                        ('pedimento_id', '=', self.id),
                        ('name', '=', complemento),
                    ])
                if not doc_dig and complemento:
                    self.env['l10n.mx.immex.pedimento.documentos.digitalizados'].create(
                        {
                            'pedimento_id': self.id,
                            'name': complemento
                        })
                self._get_acuse_edocument(complemento)
                self._get_edocument(complemento)

        for fac in self.factura_ids:
            if 'COVE' in fac.num_factura:
                self._get_acuse_edocument(fac.num_factura, 'consultarAcuseCove')
                self._get_cove(fac.num_factura, fac.response)

    @api.multi
    def _get_cove(self, cove, response):
        dom = parseString(response)
        self.message_post(body=response)
        if (dom.getElementsByTagName('contieneError')[
                0].firstChild.nodeValue or False) == 'false':

            attachment = self.env['ir.attachment'].search([
                ('name', '=', cove + '.xml'),
                ('datas_fname', '=', cove + '.xml'),
                ('res_model', '=', 'l10n.mx.immex.pedimento'),
                ('res_id', '=', self.id)
            ])
            if not attachment:
                self.env['ir.attachment'].create({
                    'name': cove + '.xml',
                    'datas': base64.encodebytes(response.encode("UTF-8")),
                    'datas_fname': cove + '.xml',
                    'res_model': 'l10n.mx.immex.pedimento',
                    'res_id': self.id,
                    'type': 'binary',
                })

            attachment = self.env['ir.attachment'].search([
                ('name', '=', cove),
                ('datas_fname', '=', cove + '.pdf'),
                ('res_model', '=', 'l10n.mx.immex.pedimento'),
                ('res_id', '=', self.id)
            ])

            if not attachment:
                xml_cove = dom.getElementsByTagName('cove')[0]

                report = self.env['ir.actions.report']._get_report_from_name(
                    'immex_gebesa.report_cove_to_pdf')
                data = {
                    'cove': xml_cove,
                    'DATOS_COVE': DATOS_COVE}
                pdf = report.render_qweb_pdf(self.id, data=data)[0]

                self.env['ir.attachment'].create({
                    'name': cove,
                    'datas': base64.encodebytes(pdf or ''),
                    'datas_fname': cove + '.pdf',
                    'res_model': 'l10n.mx.immex.pedimento',
                    'res_id': self.id,
                    'type': 'binary',
                })

        else:
            error = dom.getElementsByTagName('mensaje')[
                0].firstChild.nodeValue or False
            self.message_post(body=(
                'Error al adjuntar xml del cove %s: \n %s') % (
                cove, error))

    @api.multi
    def _get_acuse_edocument(self, complemento=None, soapaction='consultarAcuseEdocument'):
        tipo_ed = "AcuseEdocument_"
        if soapaction == 'consultarAcuseCove':
            tipo_ed = "AcuseCove_"

        name_attachment = tipo_ed + complemento

        attachment = self.env['ir.attachment'].search([
            ('name', '=', name_attachment),
            ('datas_fname', '=', name_attachment + '.pdf'),
            ('res_model', '=', 'l10n.mx.immex.pedimento'),
            ('res_id', '=', self.id)
        ])
        if attachment:
            return

        values = {
            'complemento': complemento,
            'user_name': self.env.user.company_id.partner_id.vat,
            'user_pass': self.env.user.company_id.pass_vucem,
        }
        msg = self.env['ir.qweb'].render(DESCARGAR_ACUSE, values=values)

        try:
            response_acuse = requests.request(
                "POST",
                'https://www.ventanillaunica.gob.mx:443/ventanilla-acuses-HA/ConsultaAcusesServiceWS',
                data=msg,
                headers={
                    'content-type': 'text/xml; charset=utf-8',
                    'SOAPAction': 'http://www.ventanillaunica.gob.mx/ventanilla/ConsultaAcusesService/' + soapaction,
                }
            )

        except Exception as err:
            error = tools.ustr(traceback.format_exc())
            if hasattr(error, 'name'):
                error = err.name
            elif hasattr(error, 'message'):
                error = err.message
            self.message_post(
                body=(('Ocurrio un error al consultar la partida en \
                        el sitio del VUCEM favor de notificar al \
                        Administrador del sistema %s') % error))
            return

        result = response_acuse.content[230:-45]
        dom = parseString(result)

        if dom.getElementsByTagName('error') and dom.getElementsByTagName(
                'error')[0].firstChild.nodeValue != 'false':
            error = dom.getElementsByTagName('descripcion')[0].firstChild.nodeValue or False
            self.message_post(body=(
                'Error al descargar el acuse del documento %s: \n %s') % (
                complemento, error))
            return

        filebase64 = dom.getElementsByTagName('acuseDocumento')[0].firstChild.nodeValue
        _logger.error(
            _('filebase64: %s' % filebase64))
        self.env['ir.attachment'].create({
            'name': name_attachment,
            'datas': filebase64,
            'datas_fname': name_attachment + '.pdf',
            'res_model': 'l10n.mx.immex.pedimento',
            'res_id': self.id,
            'type': 'binary',
        })

    @api.multi
    def _get_edocument(self, complemento=None):
        attachment = self.env['ir.attachment'].search([
            ('name', '=', complemento),
            ('datas_fname', '=', complemento + '.pdf'),
            ('res_model', '=', 'l10n.mx.immex.pedimento'),
            ('res_id', '=', self.id)
        ])
        if attachment:
            return

        values = {
            'complemento': complemento,
            'user_name': self.env.user.company_id.partner_id.vat,
            'user_pass': self.env.user.company_id.pass_vucem,
        }
        msg = self.env['ir.qweb'].render(DESCARGAR_EDOCUMENT, values=values)

        headers = {
            'content-type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://tempuri.org/IServicioEdocument/GetDocumento',
        }
        try:
            response = requests.request(
                "POST",
                'https://www.ventanillaunica.gob.mx/Ventanilla-HA/ServicioEdocument/ServicioEdocument.svc',
                data=msg,
                headers=headers
            )

        except Exception as err:
            error = tools.ustr(traceback.format_exc())
            if hasattr(error, 'name'):
                error = err.name
            elif hasattr(error, 'message'):
                error = err.message
            self.message_post(
                body=(('Ocurrio un error al consultar la partida en \
                    el sitio del VUCEM favor de notificar al \
                    Administrador del sistema %s') % error))
            return

        result = response.content
        dom = parseString(result)
        if dom.getElementsByTagName('TieneError') and dom.getElementsByTagName(
                'TieneError')[0].firstChild.nodeValue != 'false':
            error = dom.getElementsByTagName('Errores')[0].firstChild.nodeValue or False
            self.message_post(body=(
                'Error al descargar el documento %s: \n %s') % (
                complemento, error))
            return

        filebase64 = dom.getElementsByTagName('File')[0].firstChild.nodeValue
        _logger.error(
            _('filebase64: %s' % filebase64))
        _logger.error(
            _('result: %s' % result))

        self.env['ir.attachment'].create({
            'name': complemento,
            'datas': filebase64,
            'datas_fname': complemento + '.pdf',
            'res_model': 'l10n.mx.immex.pedimento',
            'res_id': self.id,
            'type': 'binary',
        })
