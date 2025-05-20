# Copyright 2022, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    products_services_id = fields.Many2one(
        'l10n.mx.wbl.products.services',
        string='Waybill classification',
    )
