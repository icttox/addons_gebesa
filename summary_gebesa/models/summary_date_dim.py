# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models
from dateutil.relativedelta import relativedelta

MONTH_SELECTION = [
    (1, 'January'), (2, 'February'),
    (3, 'March'), (4, 'April'),
    (5, 'May'), (6, 'June'),
    (7, 'July'), (8, 'August'),
    (9, 'September'), (10, 'October'),
    (11, 'November'), (12, 'December')]


class SummaryDateDim(models.Model):
    _name = 'summary.date.dim'
    _description = 'Date data for summaries'
    _order = "year desc, week desc"

    name = fields.Char(
        string='Name',
    )
    year = fields.Integer(
        string='Year',
    )
    month = fields.Selection(
        MONTH_SELECTION,
        string='Month',
    )
    quarter = fields.Integer(
        string='Quarter',
    )
    week = fields.Integer(
        string='Week',
    )
    inventory_ids = fields.One2many(
        'summary.inventory',
        'date_id',
        string='Summary inventory',
    )
    purchase_ids = fields.One2many(
        'summary.purchase',
        'date_id',
        string='Summary purchase',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )

    _sql_constraints = [
        ('date_uniq',
         'unique (year,week,company_id)',
         'The week of the year must be unique per company !')
    ]

    def create_new_summary(self):
        # Fecha actual
        date = fields.Date.context_today(self)
        # Fecha del domingo de la semana pasada
        date = date - relativedelta(days=date.weekday() + 1)
        # Fecha del jueves de la semana pasada
        date_dim = date - relativedelta(days=3)
        # Se toma la fecha del jueves para crear el resumen
        # dado que la primera semana del año es la que contenga
        # el primer jueves de ese año esto dado el ISO 8601

        date_id = self.create({
            'year': date_dim.year,
            'month': date_dim.month,
            'quarter': date.month // 4 + 1,
            'week': date_dim.isocalendar()[1],
            'name': str(date_dim.year) + '-' + str(date_dim.isocalendar()[1]),
        })

        self.env['summary.inventory'].create_summary_inventory(date, date_id)
        self.env['summary.purchase'].create_summary_purchase(date, date_id)
