# -*- coding: utf-8 -*-

from odoo import models, fields


class L10nMxEdiRetentionsComplement(models.Model):
    _name = 'l10n_mx_edi.retentions.complement'
    _description = "Retention Complement"

    retentions_id = fields.Many2one(
        'l10n_mx_edi.retentions',
        string="Retentions"
    )
    retention_type_code = fields.Char(
        related='retentions_id.retention_type_code',
        string='Code',
    )
    version = fields.Char(
        string='Version',
        default='1.0'
    )
    # Payment foreinger
    beneficiary = fields.Boolean(
        string='Is a beneficiary',
    )
    country_id = fields.Many2one(
        'res.country',
        string='Country of Residence',
    )
    taxpayer_type_id = fields.Many2one(
        'l10n_mx_edi.taxpayer.type',
        string='Concept',
    )
    # Disposal of Shares
    contract_intermediation = fields.Char(
        string='Contract intermediation',
    )
    earnings = fields.Float(
        string='Earnings',
    )
    losses = fields.Float(
        string='Losses',
    )
    # Dividends
    dividend_type_id = fields.Many2one(
        'l10n_mx_edi.dividend.or.profitableness.type',
        string='Dividend or Profitable type',
    )
    amount_isr_mx = fields.Float(
        string='Amount ISR Mexico',
    )
    amount_isr_foreing = fields.Float(
        string='Amount ISR Foreign',
    )
    society_type = fields.Selection(
        selection=[
            ('national_society', 'National Society'),
            ('foreing_society', 'Foreign Society')],
        string='Society Type',
        index=True,)
