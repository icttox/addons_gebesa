# -*- coding: utf-8 -*-
# © <2021> <Samuel Barron, GEBESA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import base64
import os
from xml.dom.minidom import parseString
import requests
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.immex_gebesa.models import util
from odoo.addons.immex_gebesa.models.settings import PATH

_logger = logging.getLogger(__name__)
PEM_F = os.path.join(PATH['PEM'])
CER_F = os.path.join(PATH['CER'])
CONSULTA_EDOCUMENT = 'immex_gebesa.consultar_edocument_vucem'


class L10nMxImmexPedimentoFactura(models.Model):
    _name = 'l10n.mx.immex.pedimento.factura'
    _rec_name = 'pedimento_num'
    _description = 'descripcion pendiente'

    patente = fields.Char(
        string='patente',
    )
    num_pedimento = fields.Char(
        string='Numero pedimento',
    )
    clave_aduana = fields.Char(
        string='Clave aduana',
    )
    fecha_facturacion = fields.Char(
        string='Fecha de facturación',
    )
    num_factura = fields.Char(
        string='Numero de la Factura',
    )
    termino_facturacion = fields.Char(
        string='Clave de termino de la factura',
    )
    moneda_factura = fields.Char(
        string='Clave de la moneda de la factura',
    )
    monto_usd = fields.Char(
        string='Valor en dólares',
    )
    monto_extranjera = fields.Char(
        string='Valor en moneda extranjera',
    )
    pais_facturacion = fields.Char(
        string='Clave del pais de facturación',
    )
    estado = fields.Char(
        string='Clave de la entidad federativa',
    )
    id_fiscal_proveedor = fields.Char(
        string='Identificación fiscal del proveedor',
    )
    nombre_proveedor = fields.Char(
        string='Razón social del proveedor de las mercancías',
    )
    calle_proveedor = fields.Char(
        string='Calle del domicilio del proveedor',
    )
    num_interior_proveedor = fields.Char(
        string='Numero interior del docimicilio del proveedor',
    )
    num_exterior_proveedor = fields.Char(
        string='Numero exterior del docimicilio del proveedor',
    )
    cp_proveedor = fields.Char(
        string='Código Postal del Proveedor',
    )
    ciudad_proveedor = fields.Char(
        string='Ciudad del Proveedor',
    )
    fecha_real_pago = fields.Datetime(
        string='Fecha de pago real de las contribuciones',
    )
    resumen_id = fields.Many2one(
        'l10n.mx.immex.resumen',
        string='Resumen id',
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
    )
    requests = fields.Text(
        string='Requests',
    )
    response = fields.Text(
        string='Response',
    )
    pedimento_id = fields.Many2one(
        'l10n.mx.immex.pedimento',
        string='Pedimento',
        compute='_compute_pedimento_id',
        store=True,
    )
    pedimento_num = fields.Char(
        string='Pedimento Numero',
        related='pedimento_id.pedimento_num',
        store=True,
    )
    clave_documento = fields.Char(
        string='Clave del documento',
        related='pedimento_id.clave_documento',
        store=True,
    )
    uuid = fields.Char(
        string='UUID / Folio',
    )
    factura_mercancia_ids = fields.One2many(
        'l10n.mx.immex.pedimento.factura.mercancia',
        'immex_invoice_id',
        string='Pedimento Factura Mercancia',
    )

    @api.multi
    @api.depends('clave_aduana', 'num_pedimento', 'patente')
    def _compute_pedimento_id(self):
        for ped_fac in self:
            ped_fac.pedimento_id = self.env[
                'l10n.mx.immex.pedimento'].search([
                    ('clave_aduana', '=', ped_fac.clave_aduana),
                    ('num_pedimento', '=', ped_fac.num_pedimento),
                    ('patente', '=', ped_fac.patente)])

    @api.multi
    def do_tmpfiles(self, fiel_id):
        """ Write tmp Cer file
        """
        if not fiel_id:
            raise ValidationError(
                "There is not a valid Certificate (CSD)"
                "for the company emmiter of this invoice,"
                " verify please...")

        pem_file = fiel_id.fiel_key_file_pem

        with open(PEM_F, 'wb') as pem:
            pem.write(base64.decodebytes(pem_file or ''))
            pem.close()

        cer_file = fiel_id.fiel_file

        with open(CER_F, 'wb') as cer:
            cer.write(base64.decodebytes(cer_file or ''))
            cer.close()

    def check_vucem(self):
        rfc = self.env.user.company_id.partner_id.vat

        fiel = self.env['cfdi.fiel'].search([
            ('company_id', '=', self.env.user.company_id.id),
            ('active', '=', True)], order='id',
            limit=1)

        if not fiel:
            raise ValidationError("not found fiel")
        fiel_file_pem = fiel.fiel_file_pem

        certificado = base64.decodebytes(fiel_file_pem).decode("utf-8")
        certificado = certificado.replace('-----BEGIN CERTIFICATE-----', '')
        certificado = certificado.replace('-----END CERTIFICATE-----', '')
        certificado = certificado.replace('\n', '')

        for ped in self:
            if 'COVE' in ped.num_factura:
                cadena_ori = '|' + rfc + '|' + ped.num_factura + '|'

                self.do_tmpfiles(fiel)
                cadena_fir = util.get_sello_cadena_sha256(PEM_F, cadena_ori)

                values = {
                    'user_name': rfc,
                    'user_pass': self.env.user.company_id.pass_vucem,
                    'certificado': certificado,
                    'cadena_original': cadena_ori,
                    'firma': cadena_fir.decode("utf-8"),
                    'edocument': ped.num_factura
                }
                ped.requests = self.env['ir.qweb'].render(CONSULTA_EDOCUMENT, values=values)

                try:
                    response = requests.request(
                        "POST",
                        'https://www.ventanillaunica.gob.mx/ventanilla/ConsultarEdocumentService',
                        data=ped.requests,
                        headers={
                            'content-type': 'text/xml; charset=utf-8',
                        }
                    )
                    ped.response = response.content
                    dom = parseString(ped.response)
                    ped.factura_mercancia_ids.unlink()
                    mercancias = dom.getElementsByTagName('mercancias')[0]
                    for merc in mercancias.getElementsByTagName('mercancia'):
                        self.env['l10n.mx.immex.pedimento.factura.mercancia'].create({
                            'immex_invoice_id': ped.id,
                            'descripcion': merc.getElementsByTagName(
                                'descripcionGenerica')[
                                0].firstChild.nodeValue or '',
                            'clave_uom': merc.getElementsByTagName(
                                'claveUnidadMedida')[
                                0].firstChild.nodeValue or '',
                            'moneda': merc.getElementsByTagName('tipoMoneda')[
                                0].firstChild.nodeValue or '',
                            'cantidad': merc.getElementsByTagName('cantidad')[
                                0].firstChild.nodeValue or '',
                            'valor_unitario': merc.getElementsByTagName(
                                'valorUnitario')[0].firstChild.nodeValue or '',
                            'valor_total': merc.getElementsByTagName(
                                'valorTotal')[0].firstChild.nodeValue or '',
                            'valor_dolares': merc.getElementsByTagName(
                                'valorDolares')[0].firstChild.nodeValue or ''
                        })
                    ped.uuid = dom.getElementsByTagName(
                        'numeroFacturaRelacionFacturas')[
                        0].firstChild.nodeValue or False
                except Exception as err:
                    _logger.debug("IMMEX: %s", str(err))
                    continue
                if ped.uuid:
                    invoice = self.env['account.invoice'].search([(
                        'reference', '=', ped.uuid)], limit=1,
                        order='id desc')
                    if invoice:
                        self._cr.execute("""
                            UPDATE account_invoice set
                                patente_aduanal = %s,
                                petition_number = %s,
                                clave_aduanal = %s,
                                cove = %s
                            WHERE id = %s""", (
                            ped.patente, ped.num_pedimento,
                            ped.clave_aduana, ped.num_factura,
                            invoice.id))
                        ped.invoice_id = invoice.id
                    else:
                        invoice = self.env['account.invoice'].search(['|', (
                            'number', '=', ped.uuid), (
                            'cfdi_uuid', '=', ped.uuid)], limit=1,
                            order='id desc')
                        if invoice:
                            self._cr.execute("""
                                UPDATE account_invoice set
                                    patente_aduanal = %s,
                                    petition_number = %s,
                                    clave_aduanal = %s,
                                    cove = %s
                                WHERE id = %s""", (
                                ped.patente, ped.num_pedimento,
                                ped.clave_aduana, ped.num_factura,
                                invoice.id))
                            ped.invoice_id = invoice.id
            else:
                invoice = self.env['account.invoice'].search([(
                    'cfdi_uuid', '=', ped.num_factura)])
                if invoice:
                    self._cr.execute("""
                        UPDATE account_invoice set
                            patente_aduanal = %s,
                            petition_number = %s,
                            clave_aduanal = %s
                        WHERE id = %s""", (
                        ped.patente, ped.num_pedimento,
                        ped.clave_aduana, invoice.id))
                    ped.invoice_id = invoice.id

    def import_for_data_stage(self, lines, resumen):
        for line in lines:
            line = line.replace('\r\n', '')
            line = line.replace('\x00', '')
            line = line.split("|")

            pedimento_factura = self.create({
                'patente': line[0],
                'num_pedimento': line[1],
                'clave_aduana': line[2],
                'fecha_facturacion': line[3] or None,
                'num_factura': line[4],
                'termino_facturacion': line[5],
                'moneda_factura': line[6],
                'monto_usd': line[7],
                'monto_extranjera': line[8],
                'pais_facturacion': line[9],
                'estado': line[10],
                'id_fiscal_proveedor': line[11],
                'nombre_proveedor': line[12],
                'calle_proveedor': line[13],
                'num_interior_proveedor': line[14],
                'num_exterior_proveedor': line[15],
                'cp_proveedor': line[16],
                'ciudad_proveedor': line[17],
                'fecha_real_pago': line[18],
                'resumen_id': resumen.id,
            })

            if 'COVE' in line[4]:
                pedimento_factura.check_vucem()
