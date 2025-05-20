# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    partner_ids = fields.Many2many(
        'res.partner',
        'res_company_businness_partner_rel',
        'company_id',
        'businness_partner_id',
        string='Business partners',
    )
    negative_existence = fields.Boolean(
        string='Permitir existencia negativa',
    )
    warehouse_commission = fields.Float(
        string='Warehouse commission ',
    )
    sincronize_invoices_too = fields.Boolean(
        string='Sincronize Invoices too',
    )

    @api.model
    def _company_from_partner(self, partner_id):
        company = self.sudo().search([('partner_ids', 'in', [partner_id])], limit=1)
        return company or False
