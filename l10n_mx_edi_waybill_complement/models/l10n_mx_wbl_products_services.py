# -*- coding: utf-8 -*-

from odoo import _, api, models, fields
from odoo.exceptions import UserError


class L10nMxWblProductsServices(models.Model):
    _name = 'l10n.mx.wbl.products.services'
    _description = 'Product service configuration catalog'

    code = fields.Char(
        string='Products Services',
        required=True,
    )
    name = fields.Char(
        string='Description',
    )
    dangerous = fields.Boolean(
        string='Dangerous',
    )

    threatening = fields.Selection(
        [
            ('none', 'No Peligroso'),
            ('dangerous', 'Peligroso'),
            ('quantum', 'Puede ser ambas')],
        string='Dangerous'
    )

    active = fields.Boolean(
        string='Active',
        default=True,
    )

    @api.model
    def create(self, vals):
        if not self.env.user.has_group(
                'system_administrator.group_system_administrator_gebesa') and not self.env.user.has_group('l10n_mx_edi_waybill_complement.group_products_services'):
            raise UserError(_('Only Administrator can create'))
        return super().create(vals)

    @api.multi
    def write(self, vals):
        if not self.env.user.has_group(
                'system_administrator.group_system_administrator_gebesa') and not self.env.user.has_group('l10n_mx_edi_waybill_complement.group_products_services'):
            raise UserError(_('Only administrator can edit'))
        return super().write(vals)

    @api.multi
    def unlink(self):
        if not self.env.user.has_group(
                'system_administrator.group_system_administrator_gebesa') and not self.env.user.has_group('l10n_mx_edi_waybill_complement.group_products_services'):
            raise UserError(_('Only admin can delete'))
        return super().unlink()
