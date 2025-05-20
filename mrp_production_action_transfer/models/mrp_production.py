# -*- coding: utf-8 -*-
# © <2017> <César Barrón Butista>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpProduction(models.Model):
    _name = 'mrp.production'
    _inherit = 'mrp.production'

    transfered_qty = fields.Float(
        string='Transfered quantity',
        # compute='_compute_standard_price',
        store=True,
        readonly=True,
    )
