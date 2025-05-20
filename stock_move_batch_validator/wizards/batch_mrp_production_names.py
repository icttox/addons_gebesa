# -*- coding: utf-8 -*-
# © 2017 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class BatchMrpProductionNames(models.TransientModel):
    _name = 'batch.mrp.production.names'
    _description = 'group of mrp production for procure'

    mo_names = fields.Text(
        string='MOs for validate',
        required=True,)

    @api.multi
    def action_procure_all(self):
        for rec in self:
            split_names = rec.mo_names.split(',')

            for order in split_names:
                produccion = self.env['mrp.production'].search(
                    [('name', '=', order)], limit=1)

                if produccion:
                    produccion.action_procurement_processes()
                    self.env.cr.commit()

        return True
