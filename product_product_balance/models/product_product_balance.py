# -*- coding: utf-8 -*-
# Copyright 2018, Samuel Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from odoo import api, fields, models
import pytz
from dateutil.relativedelta import relativedelta


class ProductProductBalance(models.Model):
    _name = 'product.product.balance'
    _description = 'Description'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    date_balance = fields.Date(
        string='Balance date',
        required=True,
    )
    qty = fields.Float(
        string='Quantity',
    )

    _sql_constraints = [
        ('values_uniq',
         'unique (company_id,location_id,product_id,date_balance)',
         'A record with this combination of values already exists !')
    ]

    @api.model
    def calculate_balance(self):
        date_start = datetime.today() - relativedelta(days=1)
        str_date_start = (str(date_start.year) + '-' + str(date_start.month) +
                          '-' + str(date_start.day))
        date_start = datetime.strptime(str_date_start, "%Y-%m-%d")
        # date_start = pytz.timezone(
        #     self.env.user.tz).localize(
        #     date_start, is_dst=False)
        # date_start = date_start.astimezone(pytz.timezone('UTC'))
        timezone = pytz.timezone(self._context.get('tz') or 'UTC')
        date_start = pytz.UTC.localize(date_start)
        date_start = date_start.astimezone(timezone)
        date_start = date_start + relativedelta(hours=12.0)
        date_start = date_start.strftime('%Y-%m-%d %H:%M:%S')

        date_end = datetime.today()
        str_date_end = (str(date_end.year) + '-' + str(date_end.month) + '-' +
                        str(date_end.day))

        date_end = datetime.strptime(str_date_end, "%Y-%m-%d")
        # date_end = pytz.timezone(
        #     self.env.user.tz).localize(
        #     date_end, is_dst=False)
        # date_end = date_end.astimezone(pytz.timezone('UTC'))
        date_end = pytz.UTC.localize(date_end)
        date_end = date_end.astimezone(timezone)
        date_end = date_end + relativedelta(hours=12.0)
        date_end = date_end.strftime('%Y-%m-%d %H:%M:%S')

        products = self.env['product.product'].search([], order="company_id")
        locations = self.env['stock.location'].search([(
            'usage', '=', 'internal')], order="company_id")

        for location in locations:
            for product in products:
                if (location.company_id.id !=
                        product.product_tmpl_id.company_id.id):
                    continue
                last_bal = self.env['product.product.balance'].search([
                    ('location_id', '=', location.id),
                    ('company_id', '=', location.company_id.id),
                    ('product_id', '=', product.id),
                    ('date_balance', '<', date_start)
                ], order='date_balance desc', limit=1)

                qty = 0.0

                if last_bal:
                    qty += last_bal.qty

                self._cr.execute("""
                    SELECT
                        SUM(product_uom_qty *
                            CASE WHEN location_id = %s THEN -1 ELSE 1 END)
                    FROM stock_move
                    WHERE product_id = %s
                    AND date >= %s
                    AND date < %s
                    AND (location_id = %s OR location_dest_id = %s)""", (
                    location.id, product.id, date_start,
                    date_end, location.id, location.id))
                if self._cr.rowcount:
                    res = self._cr.fetchone()
                    if res[0] is not None:
                        qty += float(res[0])

                self._cr.execute("""
                    SELECT id
                    FROM product_product_balance
                    WHERE product_id = %s AND location_id = %s
                    AND company_id = %s
                    AND date_balance = %s limit 1""", (
                    product.id, location.id, location.company_id.id,
                    str_date_start))
                if self._cr.rowcount:
                    res2 = self._cr.fetchone()
                    self._cr.execute("""
                    UPDATE product_product_balance SET qty = %s,
                    write_uid = %s, write_date = NOW()
                    WHERE id = %s""", (qty, self.env.user.id,
                                       int(res2[0])))
                else:
                    self._cr.execute("""
                        INSERT INTO product_product_balance(location_id,
                        product_id,
                        company_id,date_balance,qty,create_date,write_date,
                        create_uid,write_uid)
                        SELECT %s,%s,%s,%s,%s,
                        now(),now(),%s,%s""", (
                        location.id, product.id, location.company_id.id,
                        str_date_start, qty,
                        self.env.user.id, self.env.user.id))
