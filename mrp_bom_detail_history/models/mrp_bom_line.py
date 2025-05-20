# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        history_obj = self.env['mrp.bom.detail.history']
        bom_obj = self.env['mrp.bom']
        product_obj = self.env['product.product']
        bom = bom_obj.browse(vals_list['bom_id'])
        product = product_obj.browse(vals_list['product_id'])
        his_vals = {
            'product_master_id': bom.product_id.id,
            'upd_product_detail_id': vals_list['product_id'],
            'action': 'create',
            'user_id': self._uid,
            'action_date': fields.Datetime.now(),
            'upd_qty': vals_list['product_qty'],
            'upd_cost': product.standard_price,
            'deference': vals_list['product_qty'] * product.standard_price,
            'id_bom': res.bom_id.id,
            'id_bom_line': res.id
        }
        history_obj.create(his_vals)

        return res

    @api.multi
    def unlink(self):
        history_obj = self.env['mrp.bom.detail.history']
        for line in self:
            defe = 0 - (line.product_qty * line.product_id.standard_price)
            his_vals = {
                'product_master_id': line.bom_id.product_id.id,
                'prev_product_detail_id': line.product_id.id,
                'action': 'delete',
                'user_id': self._uid,
                'action_date': fields.Datetime.now(),
                'prev_qty': line.product_qty,
                'prev_cost': line.product_id.standard_price,
                'deference': defe,
                'id_bom': line.bom_id.id,
                'id_bom_line': line.id
            }
            history_obj.create(his_vals)

        return super().unlink()

    @api.multi
    def write(self, vals):
        history_obj = self.env['mrp.bom.detail.history']
        product_obj = self.env['product.product']
        for line in self:
            if 'product_qty' in vals or 'product_id' in vals:
                if 'product_qty' in vals.keys():
                    upd_qty = vals['product_qty']
                else:
                    upd_qty = line.product_qty
                if 'product_id' in vals.keys():
                    product_id = vals['product_id']
                else:
                    product_id = line.product_id.id

                product = product_obj.browse(product_id)
                defe = (upd_qty * product.standard_price) -\
                    (line.product_qty * line.product_id.standard_price)
                his_vals = {
                    'product_master_id': line.bom_id.product_id.id,
                    'prev_product_detail_id': line.product_id.id,
                    'upd_product_detail_id': product_id,
                    'action': 'update',
                    'user_id': self._uid,
                    'action_date': fields.Datetime.now(),
                    'prev_qty': line.product_qty,
                    'upd_qty': upd_qty,
                    'prev_cost': line.product_id.standard_price,
                    'upd_cost': product.standard_price,
                    'deference': defe,
                    'id_bom': line.bom_id.id,
                    'id_bom_line': line.id
                }
                history_obj.create(his_vals)

        return super().write(vals)
