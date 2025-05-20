# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AvailableSale(models.Model):
    _inherit = "product.product"

    available_sale = fields.Boolean("Venta disponible", default=True)
