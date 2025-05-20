# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, _, fields, models
from odoo.exceptions import UserError


class FactoringCustomer(models.Model):
    _name = 'factoring.customer'
    _inherit = ['mail.thread']
    _description = "Factoring Customer"
    _order = 'consecutive asc'
    _rec_name = 'consecutive'

    consecutive = fields.Char(
        string=_('Folio'),
        size=250,
        required=True,
        index=True,
        copy=False,
        default='New',
        track_visibility='always')

    reference = fields.Char(
        string=_('Reference'),
        size=250,
        track_visibility='onchange')

    partner_id = fields.Many2one(
        'res.partner',
        string=_('Customer'),
        track_visibility='onchange')

    journal_id = fields.Many2one(
        'account.journal',
        string=_('Bank'),
        domain="[('type', 'in', ('bank','cash'))]",
        track_visibility='onchange')

    company_id = fields.Many2one(
        'res.company',
        string=_('Company'),
        default=lambda self: self.env['res.company']._company_default_get(
            'factoring.customer'),
        track_visibility='always')

    date = fields.Date(
        string=_('Date'),
        default=fields.Date.today,
        track_visibility='always')

    invoice_ids = fields.Many2many(
        'account.invoice',
        string=_('Customer Invoices'),
        track_visibility='onchange')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')],
        string=_('Status'),
        track_visibility='onchange',
        default='draft')

    date_bank = fields.Date(
        string=_('Payment Date the Bank'),
        track_visibility='always')

    _sql_constraints = [
        ('consecutive_uniq', 'unique (consecutive)',
         'This field must be unique!')
    ]

    @api.model
    def create(self, vals):
        if vals.get('consecutive', 'New') == 'New':
            vals['consecutive'] = self.env['ir.sequence'].next_by_code(
                'factoring.customer') or '/'
        return super().create(vals)

    @api.multi
    def integrated_factoring(self):
        fac_brw = self[0]
        res = []
        res.append(fac_brw.invoice_ids and True or False)
        if not all(res):
            raise UserError(_('You can not perform factoring! \
                                    You must select at leats one bill.'))
        for fac in fac_brw.invoice_ids:
            inv = self.env['account.invoice'].search(
                          [('id', '=', fac.id)])
            inv.write({'factoring_customer_id': fac_brw.id})
        self.write({'state': 'done'})

        return res
