# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from odoo import api, fields, models


class ReportInventoryAnalysis(models.TransientModel):
    _name = 'report.inventory.analysis'
    _description = 'descripcion pendiente'

    def _get_years(self):
        lst = []
        year = datetime.now().year
        year_init = 2017
        while year_init <= year:
            lst.append((year_init, year_init))
            year_init += 1
        return lst

    name = fields.Char(
        string='Name',
        compute='_compute_name',
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
    )
    group_id = fields.Many2one(
        'product.group',
        string='Group',
    )
    line_id = fields.Many2one(
        'product.line',
        string='Line',
    )
    product_ini_id = fields.Many2one(
        'product.product',
        string='Initial Product',
    )
    product_end_id = fields.Many2one(
        'product.product',
        string='Final Product',
    )
    product_inactive = fields.Boolean(
        string='Product Inactives',
        default=False
    )
    year = fields.Selection(_get_years, string='Year')
    month = fields.Selection([
        (1, 'January'), (2, 'February'),
        (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'),
        (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'),
        (11, 'November'), (12, 'December'), ],
        string='Month',)
    only_mp = fields.Boolean(
        string='Solo productos de MP',
        default=True
    )

    @api.depends('warehouse_id', 'location_id', 'year', 'month')
    def _compute_name(self):
        for record in self:
            name = ''
            name += record.warehouse_id.name + '-'
            name += record.location_id.name + '-'
            name += str(record.year) + '-'
            name += str(record.month)
            record.name = name

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        self.location_id = False


class ReportConsumptionDate(models.TransientModel):
    _name = 'report.consumption.date'
    _description = 'descripcion pendiente'

    name = fields.Char(
        string='Name',
        compute='_compute_name',
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
    )
    group_id = fields.Many2one(
        'product.group',
        string='Group',
    )
    line_id = fields.Many2one(
        'product.line',
        string='Line',
    )
    product_ini_id = fields.Many2one(
        'product.product',
        string='Initial Product',
    )
    product_end_id = fields.Many2one(
        'product.product',
        string='Final Product',
    )
    product_inactive = fields.Boolean(
        string='Product Inactives',
        default=False
    )
    date_ini = fields.Date(
        string='Initial date',
        default=fields.Date.today)
    date_fin = fields.Date(
        string='Final date',
        default=fields.Date.today)

    @api.depends('warehouse_id', 'location_id', 'date_ini', 'date_fin')
    def _compute_name(self):
        for record in self:
            name = ''
            name += record.warehouse_id.name + '-'
            name += record.location_id.name + '-'
            name += str(record.date_ini) + '-'
            name += str(record.date_fin)
            record.name = name

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        self.location_id = False
