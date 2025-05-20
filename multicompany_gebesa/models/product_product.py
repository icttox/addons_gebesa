# Copyright 2021, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _prepare_sellers(self, params):
        # avoid to get siplierinfos without a product variant defined
        # Just not the Gebesa's way
        return self.seller_ids.filtered(lambda psi: psi.product_id)
