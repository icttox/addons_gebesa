# -*- coding: utf-8 -*-
# © 2016 Samuel Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, fields, models


class PaymentImportCfdiSupplier(models.TransientModel):
    _name = 'payment.import.cfdi.supplier'

    cfdi = fields.Binary(
        string='CFD-I',
        filters='*.xml'
    )
    state = fields.Selection(
        [('init', 'init'),
         ('ready', 'ready'),
         ('error', 'error')],
        string="State",
        default='init',
    )

    @api.multi
    def import_cfdi(self):
        payment_obj = self.env['account.payment']
        attachment_obj = self.env['ir.attachment']
        payment_ids = self._context.get('active_id', False)
        cfdi = payment_obj.get_data_import_cfdi(self.cfdi)
        for payment in payment_obj.browse(payment_ids):
            if payment.partner_id.vat != cfdi['rfc_emisor']:
                raise exceptions.ValidationError(_('El rfc del emisor (%s) no coincide con el del proveedor (%s)')% (
                    self.partner_id.vat, cfdi['rfc_emisor']))
            if self.env.user.company_id.partner_id.vat != cfdi['rfc_receptor']:
                raise exceptions.ValidationError(_('El rfc del receptor (%s) no coincide con el de la empresa (%s)')% (
                    self.env.user.company_id.partner_id.vat, cfdi['rfc_receptor']))
            if payment.amount != float(cfdi['monto']):
                raise exceptions.ValidationError(_(
                    'El monto del pago (%s) no corresponde con el del CFD-i importado (%s)')% (
                    self.amount, cfdi['monto']))
            ctx = dict(self._context)
            ctx.pop('default_type', None)
            attachment_obj.with_context(ctx).create({
                'name': payment.name + '-' + cfdi['name'] + '.xml',
                'datas': self.cfdi,
                'datas_fname': payment.name + '-' + cfdi['name'] + '.xml',
                'res_model': 'account.payment',
                'res_id': payment.id
            })
            payment.write({
                'l10n_mx_edi_original_string': cfdi['original_string'],
                'l10n_mx_edi_cfdi_name': cfdi['name'],
                'l10n_mx_edi_payment_method_id': cfdi['forma_pago']})
