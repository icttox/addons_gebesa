# -*- coding: utf-8 -*-
# © <2017> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _name = 'sale.order'
    _description = 'sale.order'

    def _search_qty_att(self, operator, value):
        res = []
        if operator and value:
            query = '''
            SELECT distinct (res_id)
            FROM ir_attachment
            WHERE res_id IN (
                SELECT res_id FROM ir_attachment
                WHERE res_model = 'sale.order'
                GROUP BY res_id HAVING Count(*)%s %s)''' % (operator, value)
            self.env.cr.execute(query)
            for inv in self.env.cr.fetchall():
                res.append(inv[0])
            return [('id', 'in', res)]
        if not value:
            query = """
                SELECT distinct(res_id)
                FROM ir_attachment
                WHERE res_id IS NOT NULL and res_model = 'sale.order'"""
            self.env.cr.execute(query)
            for inv in self.env.cr.fetchall():
                res.append(inv[0])
            if operator == '!=':
                return [('id', 'in', res)]
            if operator == '=':
                return [('id', 'not in', res)]
        return [('id', 'in', [])]

    qty_attachments = fields.Integer(
        "Attachments",
        help='Number of attachments per invoice',
        compute="count_attachments",
        store=False,
        search=_search_qty_att)

    @api.one
    def count_attachments(self):
        obj_attachment = self.env['ir.attachment']
        self.qty_attachments = obj_attachment.search_count(
            [('res_model', '=', 'sale.order'),
             ('res_id', '=', self.id,)])

    # inherit hacia la accion confirmar del sale_order para que tenga un adjunto
    @api.multi
    def action_confirm(self):
        for order in self:
            if not order.qty_attachments or order.qty_attachments == 0:
                raise UserError(_('You need to attach a Purchase Order!'))

        return super().action_confirm()
