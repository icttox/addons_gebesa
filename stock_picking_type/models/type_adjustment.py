# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class TypeAdjustment(models.Model):
    _name = 'type.adjustment'
    _description = 'Type of adjustment'
    _order = 'consecutive asc'
    _rec_name = 'description'

    @api.model
    def _default_consecutive(self):
        last_id = 0
        get_count = self.search_count([(1, '=', 1)])
        if get_count:
            last_id = get_count + 1
        else:
            last_id = 1
        consecutive = str(last_id).rjust(5, '0')
        return consecutive

    consecutive = fields.Char(
        string='Key', size=5,
        default=_default_consecutive,
        help='Key type of adjustment',
    )

    description = fields.Char(
        string='Description', size=150,
        help='Description type of adjustment'
    )

    type_adjustment = fields.Selection(
        [('input', 'Input'),
         ('output', 'Output')],
        string="Type of adjustment",
    )

    type_calculation = fields.Selection(
        [('none', 'None'),
         ('extra_outputs', 'Extra outputs'),
         ('net_changes', 'Net changes'),
         ('extra_inputs', 'Extra inputs')],
        string="Type of calculation",
    )

    account_id = fields.Many2one(
        'account.account', string='Account',
    )

    company_id = fields.Many2one(
        'res.company', string='Company',
    )

    reverse_type_id = fields.Many2one(
        'type.adjustment',
        string='Tipo contrario',
        required=True
    )

    active = fields.Boolean(
        default=True,
        help="Set active to false to hide the tax without removing it.")

    _sql_constraints = [
        ('_check_consecutive_uniq', 'unique (consecutive)',
         _(u'This field must be unique!'))
    ]
