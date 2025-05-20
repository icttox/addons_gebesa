# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    advance_id = fields.Many2one(
        'account.invoice',
        string='Advance Invoice',
    )

    amount_advance = fields.Float(
        'Amount Advance',
        digits=dp.get_precision('Account'),
        compute='_compute_amount_adv',
        store=True,
    )

    advance_ids = fields.One2many(
        'account.invoice.rel.advance',
        'invoice_id',
        string='Advance',
    )

    @api.onchange('advance_id')
    def _onchange_advance_id(self):
        advance = self.advance_id
        if advance:
            if advance.amount_residual_advance >= self.amount_total:
                self.amount_advance = self.amount_total
            else:
                self.amount_advance = advance.amount_residual_advance
        return

    @api.multi
    def update_advance(self):
        for invoice in self:
            for advance in invoice.advance_ids:
                if advance.advance_id:
                    advance._onchange_advance_id()

    @api.multi
    def action_cancel(self):
        suma = 0.0
        for inv in self:
            so_w_advnc = self.env['sale.order'].search([('advance_ids', 'in', inv.id)])
            if so_w_advnc:
                raise UserError(
                    'Esta factura se encuentra referenciada en el pedido %s, como anticipo manual, por favor primero quite la referencia a este anticipo del pedido' % so_w_advnc[0].name)
            inv_w_advnc = self.env['account.invoice'].search([('advance_ids', 'in', inv.id)])
            if inv_w_advnc:
                raise UserError(
                    'Esta factura se encuentra referenciada en la factura %s, como anticipo manual, por favor primero quite la referencia a este anticipo de la factura' % inv_w_advnc[0].number)
            for advance in inv.advance_ids:
                if advance.advance_id:
                    if inv.state == 'open':
                        suma = advance.advance_id.amount_residual_advance + advance.amount_advance
                        advance.advance_id.amount_residual_advance = suma
                        advance.advance_id.advance_applied = False
            inv.advance_ids = ''

            if inv.prepayment_move_ids:
                advance_invoice_ids = inv.prepayment_move_ids.mapped(
                    'line_ids').mapped('invoice_id')
                for advance_invoice in advance_invoice_ids:
                    advance_invoice.advance_applied = False
            return super().action_cancel()

    @api.multi
    def action_invoice_cancel(self):
        result = super().action_invoice_cancel()
        for invoice in self:
            if invoice.advance_id:
                invoice.advance_id.advance_applied = False

        return result

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        super()._onchange_partner_id()
        for partner in self:
            partner.advance_ids = ''

    @api.multi
    def button_advance(self):
        for adv in self:
            for advance in adv.advance_ids:
                if advance.advance_id:
                    ad = self.env['account.invoice.rel.advance'].search([('advance_id', '=', advance.advance_id.id)])
                    total_advance = 0.0
                    for advanced in ad:
                        if advanced.advance_id:
                            total_advance += advanced.amount_advance
                    anticipo = advanced.advance_id.amount_total - total_advance
                    self._cr.execute('UPDATE account_invoice '
                                     'SET amount_residual_advance=%s '
                                     'WHERE id = %s', (anticipo, advance.advance_id.id))
                    if anticipo <= 0:
                        self._cr.execute('UPDATE account_invoice '
                                         'SET advance_applied=%s '
                                         'WHERE id = %s', (True, advance.advance_id.id))

    @api.multi
    def action_move_create(self):
        res = super().action_move_create()
        for inv in self:
            if inv.prepayment_move_ids:
                advance_invoice_ids = self.prepayment_move_ids.mapped(
                    'line_ids').mapped('invoice_id')
                l10n_mx_edi_origin = '07|'
                for advance_invoice in advance_invoice_ids:
                    advance_invoice.advance_applied = True
                    if advance_invoice.l10n_mx_edi_cfdi_uuid:
                        l10n_mx_edi_origin += advance_invoice.l10n_mx_edi_cfdi_uuid + ','
                inv.l10n_mx_edi_origin = l10n_mx_edi_origin[:-1]
            elif inv.advance_id:
                inv.advance_id.advance_applied = True
                if inv.advance_id.l10n_mx_edi_cfdi_uuid:
                    inv.l10n_mx_edi_origin = '07|' + inv.advance_id.l10n_mx_edi_cfdi_uuid
            elif inv.advance_ids:
                total_advance = 0.0
                resta = 0.0
                inv.l10n_mx_edi_origin = '07|'
                for advance in inv.advance_ids:
                    if advance.advance_id:
                        if round(advance.amount_advance, 2) <= round(
                                advance.advance_id.amount_residual_advance, 2):
                            resta = advance.advance_id.amount_residual_advance - advance.amount_advance
                            advance.advance_id.sudo().write({
                                'amount_residual_advance': resta
                            })
                            if advance.advance_id.amount_residual_advance <= 0.0:
                                advance.advance_id.sudo().write({
                                    'advance_applied': True
                                })
                        else:
                            raise UserError(
                                'El monto de anticipo es mayor al saldo de la factura %s' % advance.advance_id.number)
                        total_advance += advance.amount_advance
                        if advance.advance_id.l10n_mx_edi_cfdi_uuid:
                            inv.l10n_mx_edi_origin += str(
                                advance.advance_id.l10n_mx_edi_cfdi_uuid) + ','
                    else:
                        raise UserError('El monto necesita un anticipo')

                if round(total_advance, 2) > round(self.amount_total, 2):
                    raise UserError(
                        'La sumatoria de las facturas de anticipo es mayor que el monto total de esta facturas')
                inv.l10n_mx_edi_origin = inv.l10n_mx_edi_origin[:-1]

            # if inv.advance_id and not inv.advance_id.sale_id:
            #     adv_id = inv.advance_id
            #     prod_adv = False
            #     tax_prod = []
            #     for line in adv_id.invoice_line_ids:
            #         deposit = self.pool['ir.values'].get_default(
            #             self._cr, self._uid, 'sale.config.settings',
            #             'deposit_product_id_setting') or False
            #         if line.product_id.id == deposit:
            #             product = self.env['product.product'].search(
            #                 [('id', '=', deposit)])
            #             prod_adv = product
            #             tax_prod = [(6, 0, [x.id for x in
            #                          line.product_id.taxes_id])]

            #     if not prod_adv:
            #         raise UserError(_('The Advance Invoice to which it refers,'
            #                           '\n does not have an Article type'
            #                           'in Advance'))

            #     inv_line_values2 = {
            #         'name': _('Aplication of advance'),
            #         'origin': inv.advance_id.number,
            #         'account_id': prod_adv.property_account_income_id.id,
            #         'price_unit': inv.amount_advance * -1,
            #         'quantity': 1.0,
            #         'discount': False,
            #         'uom_id': prod_adv.uom_id.id or False,
            #         'product_id': prod_adv.id,
            #         'invoice_line_tax_id': tax_prod,
            #         'account_analytic_id': inv.account_analytic_id.id,
            #         'invoice_id': inv.id,
            #     }
            #     inv_line_obj = self.env['account.invoice.line']
            #     inv_line_id = inv_line_obj.create(inv_line_values2)

            #     inv.advance_id.advance_applied = True

        return res
