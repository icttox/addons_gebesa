# -*- coding: utf-8 -*-

from odoo import models, fields, api


class L10nMxSenorityTable(models.Model):
    _name = 'l10n.mx.senority.table'
    _inherit = ['message.post.show.all']
    _description = 'Pending description'

    year = fields.Char(
        string='Year',
    )

    senority_line_ids = fields.One2many(
        'l10n.mx.senority.table.line',
        'senority_line_id',
    )

    name = fields.Char(
        compute='name_compute',
    )

    @api.depends('year')
    def name_compute(self):
        for record in self:
            record.name = record.year


class L10nMxSenorityTableLine(models.Model):
    _name = 'l10n.mx.senority.table.line'
    _inherit = ['message.post.show.all']
    _description = 'Pending description'

    years = fields.Integer(
        string='Years',
    )

    vacation_days = fields.Integer(
        string='Vacation days',
    )

    vacation_porcentage = fields.Float(
        string='Vacation porcentage',
    )

    xmass_bonus_days = fields.Integer(
        string='Xmass bonus days',
    )

    senority_line_id = fields.Many2one(
        'l10n.mx.senority.table',
        string='Senority',
    )
