# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        product_obj = self.env['product.product']
        for lines in self.order_line:
            tproduct_var = product_obj.search([(
                'id', '=', lines.product_id.id)])
            if tproduct_var.type == 'cotiza':
                raise ValidationError(_('This product is type quotation: %s,  not cant Validate this Sale Order') % (template_var.name))
        return super(SaleOrder, self).action_confirm()
