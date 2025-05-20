# -*- coding: utf-8 -*-
# Copyright 2021, Samuel Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    warehouse_commission = fields.Float(
        related='company_id.warehouse_commission',
        string='Warehouse commission ',
        readonly=False
    )
