# -*- coding: utf-8 -*-

from odoo import _, api, models, fields
from odoo.exceptions import UserError


class L10nMxWblPermitType(models.Model):
    _name = 'l10n.mx.wbl.permit.type'
    _description = 'Permit Type Catalog'

    code = fields.Char(
        string='Code Permit Type',
        required=True,
    )

    name = fields.Char(
        string='Name',
        required=True,
    )

    transport_id = fields.Many2one(
        'l10n.mx.wbl.transport',
        string='Transport',
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
