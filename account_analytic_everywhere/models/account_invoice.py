# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _default_account_analytic(self):
        return self.env['account.analytic.account'].search([(
            'use_salesorder', '=', True)], limit=1)

    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        default=_default_account_analytic
    )

    @api.multi
    def action_date_assign(self):
        res = super().action_date_assign()
        for inv in self:
            if inv.type in ('in_invoice', 'in_refund'):
                continue
            for line in inv.invoice_line_ids:
                if not line.account_analytic_id:
                    line.account_analytic_id = inv.account_analytic_id.id
        return res

    @api.model
    def line_get_convert(self, line, part):
        res = super().line_get_convert(line, part)
        if not res['analytic_account_id'] and self.type in (
                'out_invoice', 'out_refund'):
            res['analytic_account_id'] = self.account_analytic_id.id
        return res

    @api.multi
    def action_move_create(self):
        # import ipdb; ipdb.set_trace()
        self.line_remove()
        for inv in self:
            if inv.type in ('in_invoice') or not inv.company_id.is_manufacturer:
                inv.asigna_analytic()
        return super().action_move_create()

    def asigna_analytic(self):
        move = self.move_id

        for line in move.line_ids:
            if not line.analytic_account_id or line.analytic_account_id.id != self.account_analytic_id.id:
                line.analytic_account_id = self.account_analytic_id

    @api.onchange('purchase_id')
    def _onchange_purchase_id(self):
        self.account_analytic_id = False
        if self.purchase_id:
            self.account_analytic_id = self.purchase_id.account_analytic_id.id

    @api.multi
    def line_remove(self):
        if self.type not in ('in_invoice', 'in_refund'):
            return

        if self.invoice_line_ids:
            lines_to_remove = self.invoice_line_ids.filtered(lambda l: round(l.quantity, 3) == 0.000)
            lines_to_remove.unlink()
        return True


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _set_additional_fields(self, invoice):
        analytic = self.account_analytic_id
        super()._set_additional_fields(invoice)
        self.account_analytic_id = analytic

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super()._onchange_product_id()
        for line in self:
            analytic_id = line.invoice_id.account_analytic_id.id
            is_manufacturer = line.invoice_id.company_id.is_manufacturer
            if line.invoice_id.type in ('out_invoice', 'out_refund') and \
                    is_manufacturer and line.product_id:
                product_tmpl_id = line.product_id.product_tmpl_id
                if product_tmpl_id.type != 'service':
                    if not product_tmpl_id.family_id:
                        raise ValidationError(_(
                            "El producto %s no tiene familia asignada") %
                            line.product_id.default_code)
                    if not product_tmpl_id.family_id.analytic_id:
                        raise ValidationError(_(
                            "La familia %s no tiene asignada una cuenta analitica") %
                            product_tmpl_id.family_id.name)
                    analytic_id = product_tmpl_id.family_id.analytic_id.id
            line.account_analytic_id = analytic_id
        return res
