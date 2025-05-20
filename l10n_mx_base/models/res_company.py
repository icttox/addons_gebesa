# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, fields, models


class ResCompany(models.Model):
    """Inheritance doc"""
    _inherit = 'res.company'

    @api.depends('certificate_ids',
                 'certificate_ids.date_start',
                 'certificate_ids.date_end')
    def _compute_current_certificate(self):
        """If the company have many certificates, is returned the active
        record, by the dates in it."""
        certificate = self.env['cfdi.csd']
        date = time.strftime('%Y-%m-%d')
        for company in self:
            domain = [('date_start', '<=', date), ('date_end', '>=', date),
                      ('company_id', '=', company.id)]
            company.certificate_id = certificate.search(domain, limit=1)

    l10n_mx_locality = fields.Char(
        'Locality', related='partner_id.l10n_mx_locality',
        help='Locality configured for this partner')

    certificate_id = fields.Many2one(
        'cfdi.csd', 'Certificate',
        compute='_compute_current_certificate',
        help='Certificate active in this company, that will be used in '
        'electronic documents.')

    invoice_out_sequence_id = fields.Many2one(
        'ir.sequence', 'Invoice Out Sequence',
        help='The sequence used for invoice out numbers.')

    invoice_out_refund_sequence_id = fields.Many2one(
        'ir.sequence', 'Invoice Out Refund Sequence',
        help="The sequence used for invoice out refund numbers.")

    address_parent_company_id = fields.Many2one(
        "res.partner", 'Address Parent Company',
        domain="[('type', '=', 'invoice')]",
        help="In this field should placed the address of the parent company, "
        "independently if handled a scheme Multi-company o Multi-Address.")

    currency_provider = fields.Selection(
        selection_add=[('banxico', 'Mexican Bank')], default='banxico')

    pac_ids = fields.One2many('res.pac', 'company_id', 'PAC')
