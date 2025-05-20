# -*- coding: utf-8 -*-
# © <2017> <Samuel Barrón Butista>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    in_review = fields.Boolean(
        string='In review',
        default=False
    )
