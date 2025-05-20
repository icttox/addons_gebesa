# -*- coding: utf-8 -*-


from odoo import models, fields
from odoo.tools import pycompat


class ProductProduct(models.Model):
    _inherit = 'product.product'

    cost_usd = fields.Float(string='Cost USD')

    def revalue_cost_usd(self):
        currency_id = self.env.ref('base.USD')
        company_ids = self.env['res.company'].search([
            ('is_manufacturer', '=', True)])
        timezone = self._context.get('tz')
        timezone = pycompat.to_native(timezone)
        self_tz = self.with_context(tz=timezone)
        date = fields.Datetime.context_timestamp(self_tz, fields.datetime.today())
        date = date.strftime("%Y-%m-%d")
        for company in company_ids:
            self._cr.execute("""
                SELECT rate_mex
                FROM res_currency_rate
                WHERE currency_id = %s
                    AND CAST(name AS DATE) = %s
                    AND company_id = %s
            """, (currency_id.id, date, company.id))
            if self._cr.rowcount:
                rate = self._cr.fetchone()[0]
                product_ids = self.search([
                    ('cost_usd', '>', 0),
                    ('company_ids', 'in', (company.id))])
                for product in product_ids:
                    cost = round(product.cost_usd * rate, 6)
                    self.do_change_standard_price2([product.id], cost)
