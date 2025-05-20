# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError


class SetRepositionData(models.TransientModel):
    _name = 'set.reposition.data'
    _description = 'descripcion pendiente'

    sale_id = fields.Many2one(
        'sale.order',
        string='Sale',
    )

    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale line',
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )

    @api.multi
    def update_set_reposition_data(self):
        order_line_ids = self.env['sale.order.line'].browse(
            self._context.get('active_ids', []))
        for line in order_line_ids:
            if line.order_id.state != 'done':
                continue
            if line.order_id.partner_id.id != self.sale_id.partner_id.id:
                raise UserError("No tienen el mismo partner")
            # line.order_id.state = 'sale'
            line.write({'rep_sale_id': self.sale_id.id, 'rep_sale_line_id': self.sale_line_id.id})
            # line.order_id.state = 'done'

    @api.multi
    def clear_reposition_data(self):
        order_line_ids = self.env['sale.order.line'].browse(
            self._context.get('active_ids', []))
        order_line_ids.write({'rep_sale_id': False, 'rep_sale_line_id': False})

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        sale_line = self.env[self._context['active_model']].browse(self._context['active_id'])
        res['partner_id'] = sale_line.order_id.partner_id.id
        return res
