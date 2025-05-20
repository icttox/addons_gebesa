# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from codecs import BOM_UTF8

from lxml import objectify

import odoo.addons.decimal_precision as dp
from odoo import _, api, fields, models

BOM_UTF8U = BOM_UTF8.decode('UTF-8')


class WizardValidateUuidSat(models.TransientModel):
    _name = 'wizard.validate.uuid.sat'

    @api.model
    def default_get(self, fieldnames):
        res = super(WizardValidateUuidSat, self).default_get(fieldnames)
        invoice_obj = self.env['account.invoice']
        list_xml = []
        for invoice in invoice_obj.browse(self._context.get('active_ids', [])):
            if not invoice.xml_signed:
                continue
            invoice_state = invoice.state
            if invoice_state in ('open', 'paid'):
                invoice_state = 'Vigente'
            elif invoice_state == 'cancel':
                invoice_state = 'Cancelado'
            xml = objectify.fromstring(
                invoice.xml_signed.lstrip(BOM_UTF8U).encode("UTF-8"))
            xml_amount = xml.get('total', xml.get('Total'))
            xml_date = xml.get('fecha', xml.get('Fecha'))
            list_xml.append([0, False, {
                'name': invoice.number,
                'invoice_id': invoice.id,
                'amount': float(xml_amount),
                'number': xml.get('folio', xml.get('Folio', '')),
                'type': xml.get(
                    'tipoDeComprobante', xml.get('TipoDeComprobante', '')),
                'uuid': invoice_obj.l10n_mx_edi_get_tfd_etree(
                    xml).get('UUID', ''),
                'date': str(
                    datetime.strptime(xml_date.encode('ascii', 'replace'),
                                      '%Y-%m-%dT%H:%M:%S')),
                'vat_emitter': xml.Emisor.get(
                    'rfc', xml.Emisor.get('Rfc', '')),
                'vat_receiver': xml.Receptor.get(
                    'rfc', xml.Receptor.get('Rfc', '')),
                'invoice_state': invoice_state,
                'result': 'Pending',
            }])
        res.update({'xml_ids': list_xml})
        return res

    name = fields.Char(readonly=True)
    xml_ids = fields.Many2many(
        'xml.to.validate.line', 'wizard_xml_to_validate', 'wizard_id',
        'xml_id', 'XMLs to validate',
        help='XMLs to validate the UUID status in the SAT system.')

    @api.multi
    def check_uuid_sat(self):
        self.ensure_one()
        self.xml_ids.verify_status()
        return {
            'name': _("Validate Invoice UUID SAT"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'wizard.validate.uuid.sat',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': self._context,
        }


class XmlToValidateLine(models.TransientModel):
    _name = 'xml.to.validate.line'

    name = fields.Char(
        'Invoice Number', readonly=True,
        help='Number invoice to verify status in SAT system.')
    invoice_id = fields.Many2one(
        'account.invoice', 'Invoice', domain=([('xml_signed', '!=', False)]),
        help='Invoice from which is taken data to verify status in SAT '
        'system.')
    amount = fields.Float(
        digits=dp.get_precision('Account'),
        help='Amount in XML, value used to consult the UUID status in SAT '
        'system')
    number = fields.Char(
        help='Number found in the XML. Taken from "folio" node.')
    type = fields.Char(
        help='Type of document found in XML file.')
    uuid = fields.Char(
        string='UUID', help='UUID taken from XML on invoice.')
    date = fields.Datetime(
        help='Date when was generated the XML on invoice.')
    vat_emitter = fields.Char(
        'VAT Emitter', help='VAT emitter, taken from XML on invoice.')
    vat_receiver = fields.Char(
        'VAT Receiver', help='VAT receiver, taken from XML on invoice.')
    invoice_state = fields.Char(
        help='Invoice state in Odoo System.')
    result = fields.Char(
        'Result SAT', default='No Encontrado',
        help='Result after to send to validate XML data in SAT system.')

    @api.multi
    def verify_status(self):
        invoice_obj = self.env['account.invoice']
        for xml in self:
            result = invoice_obj._validate_xml_sat(
                xml.vat_emitter, xml.vat_receiver, xml.amount, xml.uuid)
            result = result and result.Estado or ''
            xml.write({'result': result})

    @api.onchange('invoice_id')
    def onchange_invoice_id(self):
        if not self.invoice_id.xml_signed:
            return {}
        xml = objectify.fromstring(
            self.invoice_id.xml_signed.lstrip(BOM_UTF8U).encode("UTF-8"))
        xml_amount = xml.get('total', xml.get('Total'))
        xml_date = xml.get('fecha', xml.get('Fecha'))
        invoice_state = self.invoice_id.state
        if invoice_state in ('open', 'paid'):
            invoice_state = 'Vigente'
        elif invoice_state == 'cancel':
            invoice_state = 'Cancelado'
        self.name = self.invoice_id.number
        self.amount = float(xml_amount)
        self.number = xml.get('folio', xml.get('Folio', ''))
        self.type = xml.get(
            'tipoDeComprobante', xml.get('TipoDeComprobante', ''))
        self.uuid = self.invoice_id.l10n_mx_edi_get_tfd_etree(
            xml).get('UUID', '')
        self.date = str(datetime.strptime(xml_date.encode('ascii', 'replace'),
                                          '%Y-%m-%dT%H:%M:%S'))
        self.vat_emitter = xml.Emisor.get('rfc', xml.Emisor.get('Rfc', ''))
        self.vat_receiver = xml.Receptor.get(
            'rfc', xml.Receptor.get('Rfc', ''))
        self.invoice_state = invoice_state
        self.result = 'Pending'

    @api.multi
    def show_cancel(self):
        return False  # pragma: no cover

    @api.multi
    def show_not_found(self):
        return False  # pragma: no cover

    @api.multi
    def show_done(self):
        return False  # pragma: no cover
