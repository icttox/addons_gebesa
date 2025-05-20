# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        for order in self:
            if not order.order_line:
                raise UserError(_('You cannot confirm a sales order which has \
                 no line.'))
            for line in order.order_line:
                if line.product_id.type == 'service':
                    continue
                if line.price_unit <= 0:
                    raise UserError(_('At least one of the lines of the \
                    sale order has price unit zero!' '\n Please make sure \
                    that all lines have successfully captured the unit price.')
                                    )

        return super().action_confirm()
