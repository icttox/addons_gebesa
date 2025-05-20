# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    prepayment_number = fields.Text(
        string='Number Invoice Advance',
    )

    prepayment_move_ids = fields.Many2many(
        'account.move',
        string='Accountant Move of the Advance Invoice',
    )

    @api.multi
    def action_move_create(self):
        res = super().action_move_create()
        lines_fac = []
        resul = []
        resp = []
        deposit = int(self.env[
            'ir.config_parameter'].sudo().get_param(
            'sale.default_deposit_product_id')) or False
        for line in self.invoice_line_ids:
            if line.product_id.id == deposit:
                lines_fac = line.sale_line_ids.invoice_lines
                for fact in lines_fac:
                    if fact.id != line.id:
                        if fact.invoice_id.number:
                            resul.append(str(fact.invoice_id.number))
                            self.prepayment_number = resul
                        if fact.invoice_id.move_id.id:
                            resp.append(fact.invoice_id.move_id.id)
                            self.prepayment_move_ids = resp
        return res
