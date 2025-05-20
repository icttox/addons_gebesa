# -*- coding: utf-8 -*-
# © 2024 Samuel Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    manufacturing_steps = fields.Selection([
        (1, '1 Paso'),
        (2, '2 Pasos')],
        string='Pasos de manufactura',
        related='company_id.manufacturing_steps',
        readonly=False,
        default=1)
