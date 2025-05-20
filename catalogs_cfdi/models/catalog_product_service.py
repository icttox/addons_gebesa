# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class CatalogProductService(models.Model):
    _name = 'catalog.product.service'
    _inherit = ['mail.thread']
    _description = 'Catalog Product Service'
    _order = "code asc"
    _rec_name = 'description'

    code = fields.Char(
        string='Code',
        size=10,
        track_visibility='always',
    )

    description = fields.Text(
        string='Description',
        track_visibility='onchange',
    )

    include_iva = fields.Selection(
        [('yes', 'Yes'),
         ('not', 'Not'),
         ('optional', 'Optional')],
        string="Include IVA Transferred",
        track_visibility='onchange',

    )

    include_ieps = fields.Selection(
        [('yes', 'Yes'),
         ('not', 'Not'),
         ('optional', 'Optional')],
        string="Include IEPS Transferred",
        track_visibility='onchange',

    )

    include_complement = fields.Selection(
        [('airlines', 'airlines'),
         ('foreign_exchange', 'Foreign Exchange'),
         ('iedu', 'iedu'),
         ('optional_airlines', 'Optional:airlines'),
         ('optional_donat', 'Optional:donat'),
         ('optional_obrasarte', 'Optional:obrasarte')],
        string="Include Complement",
        track_visibility='onchange',
    )
