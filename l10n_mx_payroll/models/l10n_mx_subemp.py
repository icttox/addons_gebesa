# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class L10nMxSubemp(models.Model):
    _name = 'l10n.mx.subemp'
    _inherit = ['message.post.show.all']
    _description = 'Pending description'

    year = fields.Char(
        string='Year',
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    subemp_ids = fields.One2many(
        'l10n.mx.subemp.line',
        'subemp_line_id',
    )

    name = fields.Char(
        compute='name_compute',
    )

    @api.constrains('year', 'active')
    def _check_unique_year_and_type_subemp(self):
        for subemp in self:
            subemp_ids = self.search([
                ('active', '=', True),
                ('year', '=', subemp.year),
                ('id', '!=', subemp.id)])
            if subemp_ids:
                raise ValidationError(
                    "You cannot have two moves with the same year and type!")

    @api.depends('year')
    def name_compute(self):
        for record in self:
            name = ''
            name = "Subemp monthly" + ' ' + record.year
            record.name = name


class L10nMxSubempLine(models.Model):
    _name = 'l10n.mx.subemp.line'
    _inherit = ['message.post.show.all']
    _description = 'Pending description'

    lower_limit = fields.Float(
        string='Lower limit',
    )

    subsidy_monthly = fields.Float(
        string='Fixed fee',
    )

    subemp_line_id = fields.Many2one(
        'l10n.mx.subemp',
    )
