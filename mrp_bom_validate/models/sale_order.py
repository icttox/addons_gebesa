# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        # template_obj = self.env['product.template']
        # bom_obj = self.env['mrp.bom']
        # res = super(SaleOrder, self).action_confirm()
        for order in self:
            # import pdb; pdb.set_trace()
            if order.company_id.is_manufacturer:
                for line in order.order_line:
                    bomProduct = self.env['mrp.bom'].search(
                        [('product_id', '=', line.product_id.id),
                         ('active', '=', True)])
                    if not bomProduct[0].approved:
                        raise ValidationError(
                            _('The BoM of this product is not approved: %s,  you cannot '
                              'Validate this Sale Order') % (line.product_id.default_code))
        return super(SaleOrder, self).action_confirm()
