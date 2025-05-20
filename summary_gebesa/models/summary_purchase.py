# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SummaryPurchase(models.Model):
    _name = 'summary.purchase'
    _description = 'Purchase summary by week'

    date_id = fields.Many2one(
        'summary.date.dim',
        string='Date dimension',
        required=True,
        ondelete='cascade'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
    )
    family_id = fields.Many2one(
        'product.family',
        string='Family',
    )
    group_id = fields.Many2one(
        'product.group',
        string='Group',
    )
    line_id = fields.Many2one(
        'product.line',
        string='Line',
    )
    pruchase_cost = fields.Float(
        string='Purchase cost',
    )
    pruchase_difference = fields.Float(
        string='Purchase difference',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )

    def get_query_purchase(self):
        return """
            SELECT
                partner_id,location_dest_id,
                family_id,group_id,line_id,
                SUM(cost), SUM(diff - cost)
            FROM (
                SELECT
                    sm.id,
                    sm.location_dest_id,
                    po.partner_id,
                    pt.family_id AS family_id,
                    pt.group_id AS group_id,
                    pt.line_id AS line_id,
                    pol.standard_price * pol.product_qty AS cost,
                    ROUND(COALESCE(MAX(ail.price_unit),pol.price_unit) *
                        COALESCE(rcr.rate_mex, 1) * pol.product_qty, 6) +
                        COALESCE(SUM(aml.debit), 0.00) AS diff
                FROM stock_move AS sm
                LEFT JOIN purchase_order_line AS pol ON sm.purchase_line_id = pol.id
                LEFT JOIN product_product AS pp ON pp.id = pol.product_id
                LEFT JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN purchase_order AS po ON pol.order_id = po.id
                LEFT JOIN account_invoice_line AS ail ON pol.id = ail.purchase_line_id
                LEFT JOIN account_invoice AS ai ON ail.invoice_id = ai.id
                LEFT JOIN integration_cost_gebesa AS icg ON ai.integration_id = icg.id
                LEFT JOIN account_move_line AS aml ON icg.move_id = aml.move_id
                    AND aml.product_id = pp.id AND aml.debit > 0
                    AND aml.name LIKE CONCAT('%%',ai.number,'%%')
                LEFT JOIN res_currency_rate AS rcr ON CAST(ai.date_invoice as DATE) = CAST(rcr.name as DATE)
                    AND rcr.currency_id = po.currency_id
                    AND rcr.company_id = sm.company_id
                WHERE sm.location_id IN (SELECT id FROM stock_location WHERE usage = 'supplier')
                    AND ai.state NOT IN ('cancel', 'draft')
                    AND sm.date < (CAST(CAST(%s AS DATE) + 1 AS DATE) AT TIME ZONE 'UTC' AT TIME ZONE 'America/Mexico_City')
                    AND sm.date >= CAST(CAST(%s AS DATE) - 6 AS DATE)
                    AND sm.state = 'done'
                    AND sm.company_id = %s
                GROUP BY sm.id,rcr.id,pol.id,po.id,pt.id) AS T1
            GROUP BY partner_id,location_dest_id,family_id,group_id,line_id
        """

    def create_summary_purchase(self, date, date_id):
        self.env.cr.execute(self.get_query_purchase(), (
            date, date, self.env.user.company_id.id))

        for line in self._cr.fetchall():
            self.create({
                'date_id': date_id.id,
                'partner_id': line[0],
                'location_id': line[1],
                'family_id': line[2],
                'group_id': line[3],
                'line_id': line[4],
                'pruchase_cost': line[5],
                'pruchase_difference': line[6],
            })
