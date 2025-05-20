# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.multi
    def open_produce_product(self):
        self.ensure_one()
        warehouse = self.location_dest_id.stock_warehouse_id
        employee = self.env['hr.employee'].sudo().search([(
            'user_id', '=', self._uid)])
        if warehouse not in employee.warehouse_ids:
            raise ValidationError(_("You do not have privileges to validate \
                                    in this warehouse."))
        return super().open_produce_product()
