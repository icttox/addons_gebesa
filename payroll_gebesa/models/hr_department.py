# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    stock_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Stock warehouse',
    )

    code = fields.Char(
        string='Code',
        required=True
    )

    @api.model
    def create(self, vals_list):
        if not self.env.user.has_group(
                'system_administrator.group_system_administrator_gebesa'):
            raise UserError(_('Only Administrator can create'))
        return super().create(vals_list)

    @api.multi
    def write(self, vals):
        if not self.env.user.has_group(
                'system_administrator.group_system_administrator_gebesa'):
            raise UserError(_('Only administrator can edit'))
        return super().write(vals)

    @api.multi
    def unlink(self):
        if not self.env.user.has_group(
                'system_administrator.group_system_administrator_gebesa'):
            raise UserError(_('Only admin can delete'))
        return super().unlink()
