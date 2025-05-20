# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.multi
    def action_start(self):
        for inventory in self:
            warehouse = inventory.location_id.stock_warehouse_id
            employee = self.env['hr.employee'].sudo().search(
                [('user_id', '=', self._uid)])
            if warehouse not in employee.warehouse_ids:
                raise ValidationError(_("You do not have privileges to validate \
                                      in this warehouse."))
        return super().action_start()

    @api.multi
    def action_done(self):
        for inventory in self:
            warehouse = inventory.location_id.stock_warehouse_id
            employee = self.env['hr.employee'].search(
                [('user_id', '=', self._uid)])
            if warehouse not in employee.warehouse_ids:
                raise ValidationError(_("You do not have privileges to validate \
                                      in this warehouse."))
        return super().action_done()
