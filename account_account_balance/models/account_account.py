# -*- coding: utf-8 -*-
# Copyright 2018, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class AccountAccountBalance(models.Model):
    _name = 'account.account.balance'
    _description = 'Description'

    date_balance = fields.Date(
        string='Balance date',
        required=True,
    )

    debit = fields.Float(
        string='Debit',
        required=True,
    )

    credit = fields.Float(
        string='Credit',
        required=True,
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
    )

    account_id = fields.Many2one(
        'account.account',
        string='Account',
        required=True,
    )

    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic',
    )

    _sql_constraints = [
        ('values_uniq', 'unique (company_id,account_id,account_analytic_id,date_balance)',
         'A record with this combination of values already exists !')
    ]

    @api.model
    def calculate_balance(self):

        date_to = datetime.datetime.today() - relativedelta(days=1)

        accounts = self.env['account.account'].search([])

        analytics = self.env['account.analytic.account'].search([])

        for account in accounts:
            for analytic in analytics:
                if account.company_id.id != analytic.company_id.id:
                    continue
                last_bal = self.env['account.account.balance'].search([
                    ('account_id', '=', account.id),
                    ('company_id', '=', account.company_id.id),
                    ('account_analytic_id', '=', analytic.id),
                    ('date_balance', '<', date_to)
                ], order='date_balance desc', limit=1)

                debit = 0
                credit = 0
                # lastdate = '2000-01-01'
                if last_bal:
                    debit = last_bal.debit
                    credit = last_bal.credit
                    # lastdate = last_bal.date_balance

                self._cr.execute("""
                    SELECT sum(debit) as debe, sum(credit) as haber
                    FROM account_move_line
                    WHERE account_id = %s AND analytic_account_id = %s
                    AND date >= %s limit 1""", (
                    account.id, analytic.id, date_to))

                if self._cr.rowcount:
                    res = self._cr.fetchone()
                    if res[0] is not None:
                        debit += float(res[0])
                    if res[1] is not None:
                        credit += float(res[1])

                self._cr.execute("""
                    SELECT id
                    FROM account_account_balance
                    WHERE account_id = %s AND account_analytic_id = %s
                    AND company_id = %s
                    AND date_balance = %s limit 1""", (
                    account.id, analytic.id, account.company_id.id, date_to))

                if self._cr.rowcount:
                    res2 = self._cr.fetchone()
                    self._cr.execute("""
                    UPDATE account_account_balance SET debit = %s,
                    credit = %s,
                    write_uid = %s, write_date = NOW()
                    WHERE id = %s""", (debit, credit, self.env.user.id,
                                       int(res2[0])))
                else:
                    self._cr.execute("""
                        INSERT INTO account_account_balance(account_id,
                        account_analytic_id,
                        company_id,date_balance,debit,credit,create_date,write_date,
                        create_uid,write_uid)
                        SELECT %s,%s,%s,%s,%s,%s,
                        now(),now(),%s,%s""", (
                        account.id, analytic.id, account.company_id.id,
                        date_to, debit, credit,
                        self.env.user.id, self.env.user.id))
        return True

    @api.model
    def calculate_balance2(self):
        date_copy = datetime.date.today() - relativedelta(days=2)
        date_new = datetime.date.today() - relativedelta(days=1)
        self._cr.execute("""
            INSERT INTO account_account_balance(
                create_uid, create_date, account_id, date_balance, company_id,
                write_uid, credit, write_date, debit, account_analytic_id)
            SELECT %s, NOW(), account_id, CAST(date_balance AS DATE) + CAST('1 days' AS INTERVAL),
                company_id, %s, credit, NOW(), debit, account_analytic_id
            FROM account_account_balance WHERE date_balance = %s""", (
            self.env.user.id, self.env.user.id, date_copy.strftime('%Y-%m-%d')))
        self._cr.execute("""
            SELECT
                aml.account_id,
                aml.analytic_account_id,
                aml.company_id,
                SUM(aml.debit) AS debit,
                SUM(aml.credit) AS credit
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            WHERE aml.date = %s AND am.state != 'draft'
            GROUP BY aml.account_id, aml.analytic_account_id, aml.company_id
            ORDER BY aml.company_id, aml.account_id, aml.analytic_account_id
            """, [date_new.strftime('%Y-%m-%d')])
        if self._cr.rowcount:
            lines_update = self._cr.fetchall()
            for line in lines_update:
                last_bal = self.env['account.account.balance'].search([
                    ('account_id', '=', line[0]),
                    ('company_id', '=', line[2]),
                    ('account_analytic_id', '=', line[1]),
                    ('date_balance', '=', date_new)
                ], order='date_balance desc', limit=1)
                if last_bal:
                    self._cr.execute("""
                        UPDATE account_account_balance  SET
                            debit = debit + %s,
                            credit = credit + %s,
                            write_uid = %s,
                            write_date = NOW()
                        WHERE id = %s
                        """, (line[3], line[4], self.env.user.id, last_bal.id))
                else:
                    self._cr.execute("""
                        INSERT INTO account_account_balance(account_id,
                        account_analytic_id,
                        company_id,date_balance,debit,credit,create_date,write_date,
                        create_uid,write_uid)
                        SELECT %s,%s,%s,%s,%s,%s,
                        now(),now(),%s,%s""", (
                        line[0], line[1], line[2],
                        date_new.strftime('%Y-%m-%d'), line[3], line[4],
                        self.env.user.id, self.env.user.id))


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post(self, invoice=False):
        res = super().post(invoice)
        date_today = datetime.date.today()
        for move in self:
            move_date = datetime.datetime.strptime(move.date, '%Y-%m-%d')
            move_date = move_date.date()
            if move_date < date_today:
                for line in move.line_ids:
                    date_balance = move_date
                    while date_balance < date_today:
                        last_bal = self.env['account.account.balance'].search([
                            ('account_id', '=', line.account_id.id),
                            ('company_id', '=', line.account_id.company_id.id),
                            ('account_analytic_id', '=', line.analytic_account_id.id),
                            ('date_balance', '=', date_balance)
                        ], order='date_balance desc', limit=1)
                        if last_bal:
                            self._cr.execute("""
                                UPDATE account_account_balance  SET
                                    debit = debit + %s,
                                    credit = credit + %s,
                                    write_uid = %s,
                                    write_date = NOW()
                                WHERE id = %s
                                """, (line.debit, line.credit, self.env.user.id, last_bal.id))
                        else:
                            self._cr.execute("""
                                INSERT INTO account_account_balance(account_id,
                                account_analytic_id,
                                company_id,date_balance,debit,credit,create_date,write_date,
                                create_uid,write_uid)
                                SELECT %s,%s,%s,%s,%s,%s,
                                now(),now(),%s,%s""", (
                                line.account_id.id, line.analytic_account_id.id,
                                line.account_id.company_id.id,
                                date_balance, line.debit, line.credit,
                                self.env.user.id, self.env.user.id))
                        date_balance = date_balance + relativedelta(days=1)
        return res

    @api.multi
    def button_cancel(self):
        res = super().button_cancel()
        date_today = datetime.date.today()
        for move in self:
            move_date = datetime.datetime.strptime(move.date, '%Y-%m-%d')
            move_date = move_date.date()
            if move_date < date_today:
                for line in move.line_ids:
                    date_balance = move_date
                    while date_balance < date_today:
                        last_bal = self.env['account.account.balance'].search([
                            ('account_id', '=', line.account_id.id),
                            ('company_id', '=', line.account_id.company_id.id),
                            ('account_analytic_id', '=', line.analytic_account_id.id),
                            ('date_balance', '=', date_balance)
                        ], order='date_balance desc', limit=1)
                        self._cr.execute("""
                            UPDATE account_account_balance  SET
                                debit = debit - %s,
                                credit = credit - %s,
                                write_uid = %s,
                                write_date = NOW()
                            WHERE id = %s
                            """, (line.debit, line.credit, self.env.user.id, last_bal.id))
                        date_balance = date_balance + relativedelta(days=1)
        return res
