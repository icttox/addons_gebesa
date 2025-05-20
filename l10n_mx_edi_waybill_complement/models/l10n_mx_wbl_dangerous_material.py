# -*- coding: utf-8 -*-

from odoo import _, api, models, fields
from odoo.exceptions import UserError


class L10nMxWblDangerousMaterial(models.Model):
    _name = 'l10n.mx.wbl.dangerous.material'
    _description = 'Dangerous Material configuration catalog'

    code = fields.Char(
        string="Code Dangerous Material",
        required=True,
    )

    name = fields.Char(
        string="Name",
        required=True,
    )

    division = fields.Char(
        string="Division",
    )

    active = fields.Boolean(
        string='Active',
        default=True,
    )

    @api.model
    def create(self, vals):
        if not self.env.user.has_group(
                'system_administrator.group_system_administrator_gebesa'):
            raise UserError(_('Only Administrator can create'))
        return super().create(vals)

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
