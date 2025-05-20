# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class SaleGoal(models.Model):
    _name = 'sale.goal'
    _description = 'Sale Goal'
    # _rec_name = 'year'

    name = fields.Char(
        string='Name',
        compute='_compute_name'
    )
    year = fields.Selection(
        [(2016, '2016'), (2017, '2017'), (2018, '2018'), (2019, '2019'),
         (2020, '2020'), (2021, '2021'), (2022, '2022'), (2023, '2023'),
         (2024, '2024'), (2025, '2025'), (2026, '2026'), (2027, '2027'),
         (2028, '2028'), (2029, '2029'), (2030, '2030'), (2031, '2031'),
         (2032, '2032'), (2033, '2033'), (2034, '2034'), (2035, '2035'),
         (2036, '2036'), ],
        string="Year",
    )
    sales_channel_id = fields.Many2one(
        'sales.channel',
        string='Sales channel',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partner',
    )
    goal_weekly_ids = fields.One2many(
        'sale.goal.weekly',
        'goal_id',
        string='Weekly',
    )
    goal_monthly_ids = fields.One2many(
        'sale.goal.monthly',
        'goal_id',
        string='Monthly',
    )
    goal_quarterly_ids = fields.One2many(
        'sale.goal.quarterly',
        'goal_id',
        string='Quarterly',
    )
    goal_id = fields.Many2one(
        'sale.goal',
        string='Parent goal',
    )

    _sql_constraints = [
        ('year_sales_channel', "unique(year,sales_channel_id)",
         'Sales channel already registered in this year'),
    ]

    @api.onchange('sales_channel_id')
    def _onchange_sales_channel_id(self):
        if self.sales_channel_id:
            self.partner_ids = None

    @api.onchange('partner_ids')
    def _onchange_partner_ids(self):
        if self.partner_ids:
            self.sales_channel_id = None

    @api.depends('year', 'sales_channel_id', 'partner_ids')
    def _compute_name(self):
        for goal in self:
            name = ''
            name += str(goal.year) + '/'
            if goal.sales_channel_id:
                name += goal.sales_channel_id.name
            else:
                for parntner in goal.partner_ids:
                    name += parntner.name + ','
            goal.name = name


class SaleGoalWeekly(models.Model):
    _name = 'sale.goal.weekly'
    _description = 'Sale goal weekly'

    goal_id = fields.Many2one(
        'sale.goal',
        string='Goal',
    )
    week = fields.Selection(
        [(1, '1'), (2, '2'), (3, '3'), (4, '4'),
         (5, '5'), (6, '6'), (7, '7'), (8, '8'),
         (9, '9'), (10, '10'), (11, '11'), (12, '12'),
         (13, '13'), (14, '14'), (15, '15'), (16, '16'),
         (17, '17'), (18, '18'), (19, '19'), (20, '20'),
         (21, '21'), (22, '22'), (23, '23'), (24, '24'),
         (25, '25'), (26, '26'), (27, '27'), (28, '28'),
         (29, '29'), (30, '30'), (31, '31'), (32, '32'),
         (33, '33'), (34, '34'), (35, '35'), (36, '36'),
         (37, '37'), (38, '38'), (39, '39'), (40, '40'),
         (41, '41'), (42, '42'), (43, '43'), (44, '44'),
         (45, '45'), (46, '46'), (47, '47'), (48, '48'),
         (49, '49'), (50, '50'), (51, '51'), (52, '52')],
        string="Week",
    )
    amount = fields.Float(
        string='Amount',
        digits=dp.get_precision('Product Price')
    )
    _sql_constraints = [
        ('goal_week', "unique(goal_id,week)",
         'Week already registered in this goal'),
        ('amount_cero', "check(amount != 0)", 'No amount allowed 0'),
    ]


class SaleGoalMonthly(models.Model):
    _name = 'sale.goal.monthly'
    _description = 'Sale goal monthly'

    goal_id = fields.Many2one(
        'sale.goal',
        string='Goal',
    )
    month = fields.Selection(
        [(1, 'January'), (2, 'February'), (3, 'March'),
         (4, 'April'), (5, 'May'), (6, 'June'),
         (7, 'July'), (8, 'August'), (9, 'September'),
         (10, 'October'), (11, 'November'), (12, 'December')],
        string="Month",
    )
    amount = fields.Float(
        string='Amount',
        digits=dp.get_precision('Product Price')
    )
    _sql_constraints = [
        ('goal_month', "unique(goal_id,month)",
         'Month already registered in this goal'),
        ('amount_cero', "check(amount != 0)", 'No amount allowed 0'),
    ]


class SaleGoalQuarterly(models.Model):
    _name = 'sale.goal.quarterly'
    _description = 'Sale goal quarterly'

    goal_id = fields.Many2one(
        'sale.goal',
        string='Goal',
    )
    quarter = fields.Selection(
        [(1, '1'), (2, '2'), (3, '3'), (4, '4')],
        string="Quarter",
    )
    amount = fields.Float(
        string='Amount',
        digits=dp.get_precision('Product Price')
    )
    _sql_constraints = [
        ('goal_quarterly', "unique(goal_id,quarter)",
         'Quarter already registered in this goal'),
        ('amount_cero', "check(amount != 0)", 'No amount allowed 0'),
    ]
