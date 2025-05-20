# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
'''import ipdb'''


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state_hist_ids = fields.One2many(
        'purchase.order.state.hist',
        'purchase_id',
        string='Purchase',
    )
    ''' Cada vez que una orden de presupuesto de cree registara la fecha
    en que fue creada y el estatus sera draft - no_review'''
    @api.model
    def create(self, vals):
        res = super().create(vals)

        hist_obj = self.env['purchase.order.state.hist']
        his_vals = {
            'purchase_id': res.id,
            'date': fields.Datetime.now(),
            'status_new': res.state + "-" + res.review
        }
        hist_obj.create(his_vals)
        return res

    @api.multi
    def write(self, vals):
        hist_obj = self.env['purchase.order.state.hist']
        for po in self:
            newstate = ''
            if('state' in vals.keys() or 'review' in vals.keys()):
                if 'state' in vals.keys():
                    newstate = vals['state']
                else:
                    newstate = po.state
                if 'review' in vals.keys():
                    newstate += '-' + vals['review']
                else:
                    newstate += '-' + po.review

                his_vals = {
                    'purchase_id': po.id,
                    'date': fields.Datetime.now(),
                    'status_old': po.state + "-" + po.review,
                    'status_new': newstate,
                }

                hist_obj.create(his_vals)
        return super().write(vals)
