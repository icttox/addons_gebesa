# -*- coding: utf-8 -*-
# Copyright 2018, Esther Cisneros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

class TransferRequirements(models.Model):
    _name = 'transfer.requirements'
    _inherit = ['message.post.show.all']
    _description = 'transfer'
    _order = 'consecutive asc'
    _rec_name = 'consecutive'

    consecutive = fields.Char(
        string='Folio',
        size=250,
        index=True,
        copy=False,
        default='New',
        track_visibility='always')

    color = fields.Integer()

    name_cheke = fields.Char(
        string='Check:',
    )

    responsible_id = fields.Many2one('hr.employee',
        ondelete='set null', string="Request:", index=True, )

    date = fields.Date(
        string='Date',
        default=fields.Date.today,)

    Transfer = fields.Boolean(default=True,)

    company_id = fields.Many2one('res.company',
        ondelete='set null', string="Company:", index=True,)

    bank_id = fields.Many2one('res.bank',
        ondelete='set null', string="Bank:", index=True,)

    emp_ven_id = fields.Many2one('res.partner',
        ondelete='set null', string="A favor de:", index=True,)

    quantity = fields.Float(digits=(6, 2),)

    con_obs = fields.Text(
        string='Concept y Obs:',
    )

    checkin_a = fields.Many2one('res.company',
        ondelete='set null', string="Checkin:", index=True,)

    quantity_fac = fields.Float(digits=(6, 2), string="Amount to invoice",)

    spending_id = fields.Many2one('hr.employee',
        ondelete='set null', string="Expense for: ", index=True,)

    _sql_constraints = [
        ('consecutive_uniq', 'unique (consecutive)',
         'This field must be unique!')
    ]

    @api.model
    def create(self, vals):
        if vals.get('consecutive', 'New') == 'New':
            vals['consecutive'] = self.env['ir.sequence'].next_by_code(
                'transfer.requirements') or '/'
        return super().create(vals)
