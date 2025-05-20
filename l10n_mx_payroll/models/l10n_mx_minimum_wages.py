# -*- coding: utf-8 -*-


from odoo import models, fields, api


class L10nMxMinimumWages(models.Model):
    _name = 'l10n.mx.minimum.wages'
    _inherit = ['message.post.show.all']
    _description = 'Pending description'

    type_wages = fields.Selection(
        [('a', 'A'),
         ('b', 'B'),
         ('c', 'C'),
         ('uma', 'UMA'),
         ('umi', 'UMI')],
        string='Type wages',
    )

    default = fields.Boolean(
        string='Default',
    )

    minimum_wages_line_ids = fields.One2many(
        'l10n.mx.minimum.wages.line',
        'minimum_wages_line_id',
        string='minimum wages line',
    )

    name = fields.Char(
        string='Filed Label',
        compute='name_compute'
    )

    @api.depends('type_wages')
    def name_compute(self):
        for record in self:
            name = ''
            name = "Minimum wages" + ' ' + record.type_wages
            record.name = name

    _sql_constraints = [
        ('type_wages_code_unique', 'unique (type_wages)', 'type wages must be unique.'),
        ('default_code_unique', 'unique (default)', 'default must be unique.'),
    ]


class L10nMxMinimumWagesLine(models.Model):
    _name = 'l10n.mx.minimum.wages.line'
    _inherit = ['message.post.show.all']
    _description = 'Pending description'

    validity = fields.Date(
        string='Validity'
    )

    amount = fields.Float(
        string='Amount',
    )

    minimum_wages_line_id = fields.Many2one(
        'l10n.mx.minimum.wages',
        string='minimum wages ',
    )
