# -*- coding: utf-8 -*-
# © 2017 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from datetime import datetime
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_round
from odoo.exceptions import UserError


class BatchMrpProductionPpt(models.TransientModel):
    _name = 'batch.mrp.production.ppt'
    _description = 'group of production for procurement, produce and tranfer'

    mo_names = fields.Text(
        string='MOs for validate',
        required=True,)

    @api.multi
    def action_ppt_all(self):
        for rec in self:
            split_names = rec.mo_names.split(',')

            for order in split_names:
                produccion = self.env['mrp.production'].search(
                    [('name', '=', order),
                     ('state', 'not in', ('draft', 'cancel'))], limit=1)

                if produccion:
                    produccion.action_all_processes()
