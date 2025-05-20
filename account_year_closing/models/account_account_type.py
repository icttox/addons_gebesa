# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    main_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Cuenta analitica principal',
    )

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    closing_year_journal = fields.Boolean(
        'Diario de cierre fiscal',
    )

class AccountAccountValue(models.Model):
    _name = 'account.account.value'
    _description = 'descripcion pendiente'

    @api.model
    def _get_account_not_view_domain(self):
        ids = self.env.ref('account_account_parent.data_account_type_view').ids
        return [('user_type_id', '!=', ids)]

    account_year_closing_id = fields.Many2one(
        'account.year.closing',
        string='Account Year Closing',
    )

    account_type = fields.Selection(
        [('debe', 'Debe'),
         ('haber', 'Haber')],
        string='Account Type'
    )

    account_account_closing_id = fields.Many2many(
        'account.account',
        'account_account_closing_rel',
        string='Account Account Closing',
        domain=_get_account_not_view_domain
    )
