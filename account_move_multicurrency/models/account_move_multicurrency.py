# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
# from odoo.tools.misc import profile
# from odoo.tools.profiler import profile


class AccountMoveMulticurrency(models.Model):
    _name = "account.move.multicurrency"
    _description = "Account Move Multicurrency"
    _order = 'consecutive asc'
    _rec_name = 'consecutive'

    date = fields.Date(
        default=fields.Date.today,
        required=True)

    consecutive = fields.Char(
        string='Name',
        size=250,
        required=True,
        index=True,
        copy=False,
        default='New',
        track_visibility='always')

    journal_id = fields.Many2one(
        'account.journal',
        string="Account Journal",
        required=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'account.move.multicurrency'),
        track_visibility='always'
    )

    account_move_multicurrency_line_ids = fields.One2many(
        'account.move.multicurrency.line',
        'account_move_multicurrency_id',
        string="Account Move Multicurrency Line"
    )

    account_move_id = fields.Many2one(
        'account.move',
        string="Account Move",
        copy=False,
    )

    ref = fields.Char(
        string='Reference',
        size=250,
        required=True)

    partner_id = fields.Many2one(
        'res.partner',
        string="Socio"
    )

    currency_id = fields.Many2one(
        'res.currency',
        string="Moneda"
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('done', 'Validated')],
        string='Status',
        readonly=True,
        index=True,
        default='draft',
        copy=False
    )

    _sql_constraints = [
        ('consecutive_uniq', 'unique (consecutive)',
         'This field must be unique!')
    ]

    @api.model
    def create(self, vals):
        if vals.get('consecutive', 'New') == 'New':
            vals['consecutive'] = self.env['ir.sequence'].next_by_code(
                'multicurrency') or '/'
        return super().create(vals)

    # @profile
    # @profile('/opt/odoo/prof.profile')
    @api.multi
    def action_validate(self):
        move_obj = self.env['account.move']
        am_line_obj = self.env['account.move.line']
        for multicurrency in self:
            for line in multicurrency.account_move_multicurrency_line_ids:
                if line.debit and line.credit:
                    raise UserError(_("Check your accounts. Should only be credit or debit."))
            total_credit = sum(multicurrency.account_move_multicurrency_line_ids.mapped('credit'))
            total_debit = sum(multicurrency.account_move_multicurrency_line_ids.mapped('debit'))
            if round(total_credit, 6) != round(total_debit, 6):
                raise UserError("El movimiento multimoneda esta descuadrado.")
            vals = {
                'date': multicurrency.date,
                'journal_id': multicurrency.journal_id.id,
                'ref': multicurrency.ref,
                'partner_id': multicurrency.partner_id.id
            }
            move_id = move_obj.create(vals)
            multicurrency.account_move_id = move_id.id
            company_currency = multicurrency.company_id.currency_id
            for line in multicurrency.account_move_multicurrency_line_ids:
                amount_currency = 0
                debit = line.debit
                credit = line.credit
                if company_currency.id != line.currency_id.id:
                    if line.debit != 0:
                        amount_currency = debit
                        debit = line.currency_id._convert(line.debit, company_currency, multicurrency.company_id, multicurrency.date)
                    else:
                        amount_currency = credit * -1
                        credit = line.currency_id._convert(line.credit, company_currency, multicurrency.company_id, multicurrency.date)
                account_move_line = {
                    'analytic_account_id': line.account_analytic_id.id,
                    'account_id': line.account_account_id.id,
                    'currency_id': line.currency_id.id,
                    'partner_id': line.partner_id.id,
                    'debit': round(debit, 4),
                    'credit': round(credit, 4),
                    'name': line.name,
                    'move_id': move_id.id,
                    'amount_currency': amount_currency
                }
                am_line_id = am_line_obj.with_context(check_move_validity=False).create(account_move_line)
                line.account_move_line_id = am_line_id.id
            move_id.post()
            multicurrency.state = 'done'
        return True

    @api.multi
    def unlink(self):
        for multicurre in self:
            if multicurre.state == 'done':
                raise UserError("You cannot delete account move multicurrency record whose status is: Validated")
        return super(AccountMoveMulticurrency, self).unlink()


class AccountMoveMulticurrencyLine(models.Model):
    _name = "account.move.multicurrency.line"
    _description = "Account Move Multicurrency Line"

    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string="Account Analytic",
        required=True
    )

    account_account_id = fields.Many2one(
        'account.account',
        string="Account Account",
        required=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency"
    )

    account_move_multicurrency_id = fields.Many2one(
        'account.move.multicurrency',
        string="Account Move Multicurrency"
    )

    account_move_line_id = fields.Many2one(
        'account.move.line',
        string="Account Move Line"
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Socio"
    )

    debit = fields.Monetary(required=True)

    credit = fields.Monetary(required=True)

    name = fields.Char(required=True)
