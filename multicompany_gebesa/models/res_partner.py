# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    salesrep_id = fields.Many2one(
        'sale.salesrep',
        string='REP',
    )
    salesrep_ids = fields.Many2many(
        'sale.salesrep',
        string='REPS',
    )

    def write(self, vals):
        if not self.env.user.has_group('system_administrator.group_system_administrator_gebesa'):
            partner_ids = self.env['res.company'].sudo().search([]).mapped('partner_id.id')
            if any(partner in partner_ids for partner in self.ids):
                restricted_fields = [
                    'street_name', 'street_number', 'street_number2', 'l10n_mx_edi_colony',
                    'l10n_mx_edi_colony_code', 'l10n_mx_edi_locality', 'l10n_mx_edi_locality_id',
                    'city_id', 'city', 'state_id', 'zip', 'country_id', 'vat'
                ]
                fields_to_check = [field for field in restricted_fields if field in vals]
                if fields_to_check:
                    raise UserError("No tienes permiso para editar este cliente vinculado a una empresa.")
        return super(ResPartner, self).write(vals)
