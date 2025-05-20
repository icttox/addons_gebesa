# -*- coding: utf-8 -*-

from odoo import _, api, models, fields
from odoo.exceptions import UserError


class L10nMxWblAutotransportConf(models.Model):
    _name = 'l10n.mx.wbl.autotransport.conf'
    _description = "SAT federal motor transport configuration catalog"

    code = fields.Char(
        string='Code Autotransport Conf',
        required=True,
    )

    name = fields.Char(
        string='Name',
        required=True,
    )

    tire = fields.Char(
        string='Tire',
    )

    axles = fields.Char(
        string='Axles'
    )

    active = fields.Boolean(
        string='Active',
        default=True,
    )
    gvwr = fields.Float(
        string='Peso Bruto Vehicular',
        help="Peso bruto vehicular expresado toneladas"
    )

    carry_trailer = fields.Selection(
        [
            ('none', 'No lleva'),
            ('carries', 'Lleva'),
            ('quantum', 'Puede ser ambas')],
        string='Trailer'
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
