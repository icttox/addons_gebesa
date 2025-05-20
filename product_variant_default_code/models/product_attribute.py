# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    _sql_constraints = [
        ('number_uniq', 'unique(name)',
         _('Attribute Name must be unique!'))]
