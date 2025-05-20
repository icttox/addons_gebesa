# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    id_ns = fields.Integer(
        'Internal ID in Netsuite',
    )


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    id_ns = fields.Integer(
        'Internal ID in Netsuite:'
    )
