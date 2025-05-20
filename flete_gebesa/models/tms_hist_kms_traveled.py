# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class TmsTireKmsTraveledHist(models.Model):
    _name = 'tms.hist.kms.traveled'
    _order = 'date desc'
    _description = 'descripcion pendiente'

    tms_expense_id = fields.Many2one(
        'tms.expense',
        string='Travel Expense'
    )

    kms_traveled = fields.Float(
        string='KMS Traveled',
    )

    date = fields.Date(
        string="Date"
    )

    tire_id = fields.Many2one(
        'tires',
        string='Tires',
        required=True,
    )
