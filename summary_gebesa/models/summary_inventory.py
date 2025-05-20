# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SummaryInventory(models.Model):
    _name = 'summary.inventory'
    _description = 'Inventory summary by week'

    date_id = fields.Many2one(
        'summary.date.dim',
        string='Date dimension',
        required=True,
        ondelete='cascade'
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
    net_cost = fields.Float(
        string='Costo',
    )
    net_in_out = fields.Float(
        string='In/Out',
    )
    net_revaluation = fields.Float(
        string='Revaluation',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )

    def get_query_cost(self):
        return """
            SELECT
                sl.id AS location_id,
                pf.id AS family_id,
                pg.id AS group_id,
                pl.id AS line_id,
                ROUND(SUM(CAST((sm.product_qty * COALESCE(
                    pph.cost, ip_cost.value_float, 0.00)) AS NUMERIC) *
                        CASE WHEN sm.location_id = sm.location_dest_id THEN 0
                            WHEN sm.location_dest_id = sl.id THEN 1
                            ELSE -1 END), 6) AS net_cost,
                ROUND(SUM(CAST((sm.product_qty * COALESCE(
                    pph.cost, ip_cost.value_float, 0.00)) AS NUMERIC) *
                        CASE WHEN sl.usage != 'inventory'
                            OR sm.location_id = sm.location_dest_id
                            OR sm.date < CAST(CAST(%s AS DATE) - 6 AS DATE) THEN 0
                        WHEN sm.location_dest_id = sl.id THEN 1
                        ELSE -1 END), 6) AS net_in_out
            FROM stock_location AS sl
            INNER JOIN stock_move AS sm ON (
                sm.location_id = sl.id OR sm.location_dest_id = sl.id)
                AND sm.date < (CAST(CAST(%s AS DATE) + 1 AS DATE) AT TIME ZONE 'UTC' AT TIME ZONE 'America/Mexico_City')
                AND sm.state = 'done'
            JOIN product_product AS pp ON sm.product_id = pp.id
            JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
            JOIN product_template_res_company_assignment_rel AS ptrcar ON pt.id = ptrcar.product_template_id
                AND ptrcar.res_company_assignment_id = sl.company_id
            LEFT JOIN product_family AS pf ON pt.family_id = pf.id
            LEFT JOIN product_group AS pg ON pt.group_id = pg.id
            LEFT JOIN product_line AS pl ON pt.line_id = pl.id

            LEFT JOIN ir_property AS ip_cost ON CONCAT('product.product,', pp.id) = ip_cost.res_id
                AND ip_cost.name='standard_price' AND ptrcar.res_company_assignment_id = ip_cost.company_id
            LEFT JOIN (
                SELECT product_id, MAX(id) AS id
                FROM product_price_history
                WHERE datetime < (CAST(CAST(%s AS DATE) + 1 AS DATE) AT TIME ZONE 'UTC' AT TIME ZONE 'America/Mexico_City')
                    AND company_id = %s
                GROUP BY product_id
            ) AS pphM ON pp.id = pphM.product_id
            LEFT JOIN product_price_history AS pph ON pp.id = pph.product_id AND pphM.id = pph.id
            WHERE sl.company_id = %s
                AND (sl.stock_warehouse_id IS NOT NULL
                    OR sl.usage IN ('transit', 'inventory'))
            GROUP BY sl.id, pf.id, pg.id, pl.id
            HAVING ROUND(SUM(CAST((sm.product_qty * COALESCE(pph.cost, ip_cost.value_float, 0.00)) AS NUMERIC) *
                      CASE  WHEN sm.location_id = sm.location_dest_id THEN 0
                            WHEN sm.location_dest_id = sl.id THEN 1 ELSE -1 END), 6) != 0.000000
        """

    def get_query_revaluation(self):
        return """
            SELECT
                sl.id AS location_id,
                pt.family_id AS family_id,
                pt.group_id AS group_id,
                pt.line_id AS line_id,
                ROUND(SUM(aml.debit - aml.credit), 6) AS amt_rev
            FROM account_move_line AS aml
            LEFT JOIN account_move AS am ON aml.move_id = am.id
            LEFT JOIN stock_location AS sl ON am.location_id = sl.id
            LEFT JOIN product_product AS pp ON aml.product_id = pp.id
            LEFT JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
            WHERE aml.name like 'Standard Price changed%%for existing in%%'
                AND aml.account_id IN (
                    SELECT CAST(split_part(value_reference, ',', 2) AS INT)
                    FROM ir_property
                    WHERE name IN (
                            'property_account_expense_id',
                            'property_account_expense_id',
                            'property_account_expense_categ_id',
                            'property_account_expense_categ_id')
                        AND company_id = %s
                    GROUP BY value_reference)
                AND aml.date >= CAST(%s - 6 AS DATE)
                AND aml.date <= %s
                AND aml.company_id = %s
            GROUP BY sl.id, pt.family_id, pt.group_id, pt.line_id
        """

    def create_summary_inventory(self, date, date_id):

        self.env.cr.execute(self.get_query_cost(), (
            date, date, date, self.env.user.company_id.id,
            self.env.user.company_id.id))

        for line in self._cr.fetchall():
            self.create({
                'date_id': date_id.id,
                'location_id': line[0],
                'family_id': line[1],
                'group_id': line[2],
                'line_id': line[3],
                'net_cost': line[4],
                'net_in_out': line[5],
            })

        self.env.cr.execute(self.get_query_revaluation(), (
            self.env.user.company_id.id, date, date,
            self.env.user.company_id.id))

        for line in self._cr.fetchall():
            summary = self.search([
                ('date_id', '=', date_id.id),
                ('location_id', '=', line[0]),
                ('family_id', '=', line[1]),
                ('group_id', '=', line[2]),
                ('line_id', '=', line[3])])
            if summary:
                summary.write({
                    'net_revaluation': line[4],
                })
            else:
                self.create({
                    'date_id': date_id.id,
                    'location_id': line[0],
                    'family_id': line[1],
                    'group_id': line[2],
                    'line_id': line[3],
                    'net_revaluation': line[4],
                })
