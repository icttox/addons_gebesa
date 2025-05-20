# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
'''import ipdb'''


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    state_hist_ids = fields.One2many(
        'mrp.production.state.hist',
        'production_id',
        string='Production',
    )
    ''' Cada vez que una orden de presupuesto de cree registara la fecha
    en que fue creada y el estatus sera draft - no_review'''
    @api.model
    def create(self, values):
        res = super(MrpProduction, self).create(values)

        hist_obj = self.env['mrp.production.state.hist']
        his_vals = {
            'production_id': res.id,
            'date': fields.Datetime.now(),
            'status_new': res.state + "-" + res.availability
        }
        hist_obj.create(his_vals)
        return res

    @api.multi
    def write(self, vals):
        hist_obj = self.env['mrp.production.state.hist']
        for po in self:
            newstate = ''
            if('state' in vals.keys() or 'availability' in vals.keys()):
                if 'state' in vals.keys():
                    newstate = vals['state']
                else:
                    newstate = po.state
                if 'availability' in vals.keys():
                    newstate += '-' + vals['availability']
                else:
                    newstate += '-' + po.availability

                his_vals = {
                    'production_id': po.id,
                    'date': fields.Datetime.now(),
                    'status_old': po.state + "-" + po.availability,
                    'status_new': newstate,
                }

                hist_obj.create(his_vals)
        return super(MrpProduction, self).write(vals)
