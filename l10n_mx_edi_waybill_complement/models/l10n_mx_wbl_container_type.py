# -*- coding: utf-8 -*-

from odoo import _, api, models, fields
from odoo.exceptions import UserError


class L10nMxWblContainerType(models.Model):
    _name = 'l10n.mx.wbl.container.type'
    _description = 'Container Type configuration catalog'

    code = fields.Char(
        string='Code Container Type',
        required=True,
    )

    name = fields.Char(
        string='Name',
        required=True,
    )

    description = fields.Text(
        string='Description'
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
