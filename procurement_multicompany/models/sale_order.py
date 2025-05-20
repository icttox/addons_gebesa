# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_done(self):
        res = super(SaleOrder, self).action_done()
        for order in self:
            if not order.company_id.is_manufacturer:
                ctx = self.env.context.copy()
                ctx['force_sale_order'] = order
                self.env['procurement.group'].with_context(
                    ctx)._procure_orderpoint_confirm(
                    use_new_cursor=self._cr.dbname,
                    company_id=order.company_id.id)
        return res
