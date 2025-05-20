# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    # @api.multi
    # @api.depends('rate_ids.rate')
    # def _compute_current_rate(self):
    #     date = self._context.get('date') or fields.Date.today()
    #     company_id = self._context.get('company_id') or self.env['res.users']._get_company().id
    #     # the subquery selects the last rate before 'date' for the given currency/company
    #     query = """SELECT c.id, (SELECT r.rate FROM res_currency_rate r
    #                               WHERE r.currency_id = c.id AND CAST(r.name AS DATE) <= %s
    #                                 AND (r.company_id IS NULL OR r.company_id = %s)
    #                            ORDER BY r.company_id, r.name DESC
    #                               LIMIT 1) AS rate
    #                FROM res_currency c
    #                WHERE c.id IN %s"""
    #     self._cr.execute(query, (date, company_id, tuple(self.ids)))
    #     currency_rates = dict(self._cr.fetchall())
    #     for currency in self:
    #         currency.rate = currency_rates.get(currency.id) or 1.0

    # def _get_conversion_rate(self, from_currency, to_currency):
    #     # if context is None:
    #     #     context = {}
    #     # ctx = context.copy()
    #     # if 'date' in ctx.keys():
    #     #     if ctx['date']:
    #     #         if len(ctx['date']) < 11:
    #     #             ctx['date'] = ctx['date'] + ' 23:00:00'
    #     from_currency = self.browse(cr, uid, from_currency.id, context=ctx)
    #     to_currency = self.browse(cr, uid, to_currency.id, context=ctx)
    #     return to_currency.rate / from_currency.rate


class ResCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'

    rate_mex = fields.Float(
        string='Rate mexico',
        digits=(12, 6),
    )

    @api.onchange('rate_mex')
    def _onchange_rate_mex(self):
        if self.rate_mex != 0.00:
            self.rate = 1 / self.rate_mex
        else:
            self.rate = 0.00
