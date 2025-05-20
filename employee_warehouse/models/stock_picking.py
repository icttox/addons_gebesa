# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def button_validate(self):
        for picking in self:
            if picking.location_dest_id.usage in ('customer', 'transit'):
                warehouse = picking.location_id.stock_warehouse_id
            else:
                warehouse = picking.location_dest_id.stock_warehouse_id
            employee = self.env['hr.employee'].sudo().search(
                [('user_id', '=', self._uid)])
            if warehouse:
                if warehouse not in employee.warehouse_ids:
                    raise ValidationError(_("You do not have privileges to validate \
                                            in this warehouse."))
        return super().button_validate()
