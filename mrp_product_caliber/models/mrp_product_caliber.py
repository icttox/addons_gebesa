# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models, fields
from odoo.addons import decimal_precision as dp


class MrpProductCaliber(models.Model):
    _name = 'mrp.product.caliber'
    _description = "Calibers"
    _order = 'key_caliber asc'
    _rec_name = 'name_caliber'

    key_caliber = fields.Char(
        string='Key Caliber',
    )

    name_caliber = fields.Char(
        string='Name Caliber',
    )

    espesor_mm = fields.Float(
        string='Density MM',
        digits=dp.get_precision('Product Unit of Measure'),
    )

    espesor_pgs = fields.Float(
        string='Density PGS',
        digits=dp.get_precision('Product Unit of Measure'),
    )

    peso_kg = fields.Float(
        string='Weight KG',
        digits=dp.get_precision('Product Unit of Measure'),
    )

    peso_lb = fields.Float(
        string='Weight LB',
        digits=dp.get_precision('Product Unit of Measure'),
    )

    _sql_constraints = [
        ('default_uniq', 'unique (key_caliber)',
         _('The field Key Caliber must be unique!'))
    ]
