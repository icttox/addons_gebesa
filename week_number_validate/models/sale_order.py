# -*- coding: utf-8 -*-
# © <2017> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    date_validator = fields.Datetime(
        string='Date Validator'
    )
    week_number = fields.Char(
        'Número de Semana',
    )

    @api.multi
    def action_done(self):
        res = super().action_done()
        for values in self:
            date_string = fields.Datetime.now()
            # date = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
            week = str(date_string.isocalendar()[0]) + '-' + 'W' + str(
                date_string.isocalendar()[1]).zfill(2)
            values.date_validator = date_string
            values.week_number = week
        return res
