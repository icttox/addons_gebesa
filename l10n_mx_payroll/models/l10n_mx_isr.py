# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class L10nMxIsr(models.Model):
    _name = 'l10n.mx.isr'
    _inherit = ['message.post.show.all']
    _description = 'Pending description'

    year = fields.Char(
        string='Year',
    )

    type_isr = fields.Selection(
        [('month', 'Month'),
         ('year', 'Year')],
        string='Type',
        default='month',
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    isr_detail_ids = fields.One2many(
        'l10n.mx.isr.detail',
        'isr_detail_id',
    )

    name = fields.Char(
        compute='name_compute',
    )

    @api.constrains('year', 'type_isr', 'active')
    def _check_unique_year_and_type_isr(self):
        for isr in self:
            isr_ids = self.search([
                ('active', '=', True),
                ('year', '=', isr.year),
                ('type_isr', '=', isr.type_isr),
                ('id', '!=', isr.id)])
            if isr_ids:
                raise ValidationError(
                    "You cannot have two moves with the same year and type!")

    @api.depends('year', 'type_isr')
    def name_compute(self):
        for record in self:
            if record.type_isr == 'month':
                name = "Month"
            else:
                name = "Year"
            record.name = record.year + ' ' + name


class L10nMxIsrDetail(models.Model):
    _name = 'l10n.mx.isr.detail'
    _inherit = ['message.post.show.all']
    _description = 'Pending description'

    decimal_lower_limit = fields.Float(
        string='Decimal lower limit',
    )

    fixed_fee = fields.Float(
        string='Fixed fee',
    )

    surplus_percentage = fields.Float(
        string='surplus percentage',
    )

    isr_detail_id = fields.Many2one(
        'l10n.mx.isr',
    )
