# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def split_sales_order(self):
        for order in self:
            if order.state in ('draft', 'sent'):
                default = {
                    'order_line': False,
                    'client_order_ref': order.client_order_ref,
                    'date_order': order.date_order,
                }
                order_split = []
                order_split.append(order)
                count = 1
                attachment = self.env['ir.attachment'].search([
                    ('res_model', '=', 'sale.order'),
                    ('res_id', '=', order.id)])
                while len(order.order_line) > 100:
                    new_order = order.copy(default)
                    lines = self.env['sale.order.line'].search([
                        ('order_id', '=', order.id)], order='id', limit=100)
                    lines.write({'order_id': new_order.id})
                    for att in attachment:
                        att.copy({'res_id': new_order.id})
                    order_split.append(new_order)
                    count += 1

    @api.multi
    def action_confirm(self):
        planner = self.env.ref('sale_order_planner.product_generic_planner')
        for order in self:
            for line in order.order_line:
                if line.product_id == planner:
                    raise UserError(_('You cannot validate this budget because you have a planner product.'))
        return super().action_confirm()
