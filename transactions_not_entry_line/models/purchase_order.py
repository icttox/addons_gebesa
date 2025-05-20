# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_confirm(self):
        for po in self:
            if not po.order_line:
                raise UserError(_('You cannot confirm a purchase order without \
                 any purchase order line.'))
            for line in po.order_line:
                if line.price_unit <= 0:
                    raise UserError(_('At least one of the lines of the \
                    purchase order has price unit zero!' '\n Please make sure \
                    that all lines have successfully captured the unit price.')
                                    )

        return super().button_confirm()
