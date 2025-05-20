# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    warehouse_ids = fields.Many2many(
        'stock.warehouse',
        string='Warehouses',

    )

    default_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Default warehouse',
    )

    @api.onchange('warehouse_ids', 'default_warehouse_id')
    def _onchange_warehouse_ids_and_default_warehouse_id(self):
        if self.default_warehouse_id.id is False:
            return {}
        if self.default_warehouse_id not in self.warehouse_ids:
            return {
                'warning': {
                    'title': _(u"Invalid defaul warehouse"),
                    'message': _(u"The default warehouse must be selected in\
                                  the warehouse of employee"),
                },
            }

    @api.constrains('warehouse_ids', 'default_warehouse_id')
    def _check_default_warehouse_in_warehouses(self):
        for employee in self:
            if employee.default_warehouse_id.id is False:
                return {}
            if employee.default_warehouse_id not in employee.warehouse_ids:
                raise ValidationError(
                    _(u"The default warehouse must be selected in the \
                      warehouse of employee"))
