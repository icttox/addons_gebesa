# Copyright 2023, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models
from dateutil.relativedelta import relativedelta

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_weekly_consume(self, month_sample, location_id):
        dateend = fields.Date.today()
        dateini = dateend + relativedelta(months=-month_sample)

        params = [self.id, location_id, dateini.strftime('%Y-%m-%d'), dateend.strftime('%Y-%m-%d')]

        query = """
            SELECT SUM(sm.product_qty) as qtytotal
            FROM stock_move as sm
            WHERE sm.product_id = %s
            AND sm.location_id = %s
            AND sm.state = 'done'
            AND sm.location_dest_id not in (5, 8, 9)
            AND sm.date >= %s
            AND sm.date <= %s
        """

        self.env.cr.execute(query, tuple(params))
        totalized = self.env.cr.dictfetchall()

        days = abs(dateend - dateini).days

        weekly = 0.00
        if totalized[0]['qtytotal']:
            weekly = round(totalized[0]['qtytotal'] / (days // 7), 6)

        return weekly
