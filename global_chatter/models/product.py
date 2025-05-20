# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = ['message.post.show.all', 'product.product']


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['message.post.show.all', 'product.template']
