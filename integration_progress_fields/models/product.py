# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    numctrl_progress = fields.Integer(
        'Num. Ctrl. Progress',
    )

    num_package = fields.Integer(
        'Number Packages',
    )

    # _sql_constraints = [
    #    ('default_uniq', 'unique (default_code)',
    #     _('The field Num. Ctrl. Progress must be unique!'))
    # ]


class ProductProduct(models.Model):
    _inherit = 'product.product'

    numctrl_progress = fields.Integer(
        'Num. Ctrl. Progress',
    )

    # _sql_constraints = [
    #    ('default_uniq', 'unique (default_code)',
    #     _('The field Num. Ctrl. Progress must be unique!'))
    # ]
