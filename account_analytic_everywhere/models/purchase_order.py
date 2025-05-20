# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        # related='picking_type_id.warehouse_id.account_analytic_id',
        string='Analytic Account',
        compute='_compute_account_analytic_id',
        store=True,
    )

    @api.depends('picking_type_id')
    def _compute_account_analytic_id(self):
        for purchase in self:
            warehouse = purchase.picking_type_id.warehouse_id
            purchase.account_analytic_id = warehouse.account_analytic_id.id

    @api.multi
    def action_view_invoice(self):
        res = super().action_view_invoice()
        if self.account_analytic_id:
            res['context']['default_account_analytic_id'] = self.account_analytic_id.id
        return res
