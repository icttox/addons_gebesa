# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SupplierIncident(models.Model):
    _name = 'supplier.incident'
    _inherit = ['mail.thread']
    _description = "Suppliers Incidences"
    _order = 'date desc'
    _rec_name = 'consecutive'

    consecutive = fields.Char(
        string='Folio',
        size=250,
        required=True,
        index=True,
        copy=False,
        default='New',
        track_visibility='always')

    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        track_visibility='onchange')

    user_id = fields.Many2one(
        'res.users',
        string='Reports',
        default=lambda self: self._uid,
        track_visibility='onchange')

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'supplier_incident'),
        track_visibility='always')

    description = fields.Text(
        string='Description',
        required=True,
        track_visibility='onchange'
    )

    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        track_visibility='always')

    state = fields.Selection(
        [('open', 'Open'),
         ('close', 'Closed')],
        'Status',
        default='open',
        required=True,
        copy=False,
        track_visibility='onchange')

    @api.model
    def create(self, vals):
        if vals.get('consecutive', 'New') == 'New':
            vals['consecutive'] = self.env['ir.sequence'].next_by_code(
                'supplier.incident') or '/'
        return super().create(vals)

    @api.multi
    def action_closed(self):
        self.write({'state': 'close'})
        return True
