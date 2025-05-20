# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Contrarecibo(models.Model):
    _name = 'contrarecibo'
    _inherit = ['mail.thread']
    _description = "Supplier Contrarecibo"
    _order = 'consecutive asc'
    _rec_name = 'consecutive'

    consecutive = fields.Char(
        string='Folio',
        size=250,
        required=True,
        index=True,
        copy=False,
        default='New',
        track_visibility='always')

    name = fields.Char(
        string='Name',
        size=250,
        track_visibility='onchange')

    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        track_visibility='onchange')

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'contrarecibo'),
        track_visibility='always')

    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        track_visibility='always')

    invoice_ids = fields.Many2many(
        'account.invoice',
        string='Supplier Invoices',
        track_visibility='onchange')

    _sql_constraints = [
        ('consecutive_uniq', 'unique (consecutive)',
         'This field must be unique!')
    ]

    @api.model
    def create(self, vals):
        if vals.get('consecutive', 'New') == 'New':
            vals['consecutive'] = self.env['ir.sequence'].next_by_code(
                'contrarecibo') or '/'
        return super().create(vals)
