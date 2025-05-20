# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, _
from dateutil.relativedelta import relativedelta


class StockReportByLocationPrepare(models.TransientModel):
    _name = 'stock.report.quantity.by.location.prepare'
    _description = 'Stock Report Quantity By Location Prepare'

    location_ids = fields.Many2many(comodel_name='stock.location',
                                    string='Locations',
                                    required=True)

    def open(self):
        self.ensure_one()
        self._compute_stock_report_by_location()
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'pivot,tree',
            'name': _('Stock Report by Location'),
            'context': {'search_default_quantity_gt_zero': 1,
                        'group_by_no_leaf': 1, 'group_by': []},
            'res_model': 'stock.report.quantity.by.location',
            'domain': [('wiz_id', '=', self.id)],
        }
        return action

    def _get_monthly_consume(self, product_id, location_id):

        dateend = fields.Date.today()
        dateini = dateend + relativedelta(months=-12)

        params = [product_id, location_id, dateini.strftime('%Y-%m-%d'), dateend.strftime('%Y-%m-%d')]

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
        yearly = self.env.cr.dictfetchall()

        # outputs = self.env['stock.move'].search([
        #     ('product_id', '=', product_id),
        #     ('location_id', '=', location_id),
        #     ('state', '=', 'done'),
        #     ('date', '>=', dateini),
        #     ('date', '<=', dateend),
        #     ('location_dest_id', 'not in', (5, 8, 9))
        # ])

        # yearly = sum(outputs.mapped('product_qty'))
        monthly = 0.00
        if yearly[0]['qtytotal']:
            monthly = round(yearly[0]['qtytotal'] / 12, 6)
        return monthly

    def _compute_stock_report_by_location(self):
        self.ensure_one()
        recs = []
        origin_map = {
            'national': 'Nacional',
            'import': 'Importación',
            'internal_process': 'Proceso interno',
            'external_machine': 'Maquila externa'
        }

        rotation_map = {
            'recurrent': 'Habitual',
            'special': 'Especial'
        }

        for loc in self.location_ids:
            quant_groups = self.env['stock.quant'].read_group(
                [('location_id', 'child_of', [loc.id])],
                ['quantity', 'product_id'],
                ['product_id'])
            mapping = dict(
                [(quant_group['product_id'][0],
                  quant_group['quantity'])
                 for quant_group in quant_groups]
            )
            products = self.env['product.product'].search(
                [('id', 'in', [(quant_group['product_id'][0])
                 for quant_group in quant_groups])])
            for product in products:
                origen = origin_map.get(product.product_origin, 'Sin definir')
                rotacion = rotation_map.get(product.rawmat_rotation, 'Sin definir')

                monthly_qty = self._get_monthly_consume(product.id, loc.id)
                montly_cost = (monthly_qty * product.standard_price)
                total_cost = (product.standard_price * mapping.get(product.id, 0.0))
                months_inv = 0
                if abs(round(montly_cost, 2)) > 0.00:
                    months_inv = total_cost / montly_cost

                r = self.env['stock.report.quantity.by.location'].create({
                    'product_id': product.id,
                    'product_category_id': product.categ_id.id,
                    'uom_id': product.uom_id.id,
                    'quantity': mapping.get(product.id, 0.0),
                    'location_id': loc.id,
                    'wiz_id': self.id,
                    'default_code': product.default_code,
                    'product_family_id': product.family_id.id,
                    'product_group_id': product.group_id.id,
                    'product_line_id': product.line_id.id,
                    'product_type_id': product.type_id.id,
                    'product_categ_geb_id': product.category_geb_id.id,
                    'std_cost': product.standard_price,
                    'total_cost': total_cost,
                    'product_origin': origen,
                    'rawmat_rotation': rotacion,
                    'total_consume_cost': montly_cost,
                    'months_inventory': months_inv,
                })
                recs.append(r.id)
        return recs


class StockReportQuantityByLocation(models.TransientModel):
    _name = 'stock.report.quantity.by.location'
    _description = 'Stock Report By Location'

    wiz_id = fields.Many2one(
        comodel_name='stock.report.quantity.by.location.prepare')

    product_id = fields.Many2one(
        comodel_name='product.product',
        required=True,
    )

    product_category_id = fields.Many2one(
        comodel_name='product.category',
        string='Product Category',
    )

    location_id = fields.Many2one(
        comodel_name='stock.location',
        required=True,
    )

    product_family_id = fields.Many2one(
        comodel_name='product.family',
        string='Product Family',
    )

    product_group_id = fields.Many2one(
        comodel_name='product.group',
        string='Product Group',
    )

    product_line_id = fields.Many2one(
        comodel_name='product.line',
        string='Product Line',
    )

    product_type_id = fields.Many2one(
        comodel_name='product.type',
        string='Product Type',
    )

    product_categ_geb_id = fields.Many2one(
        comodel_name='product.category.company.geb',
        string='Product Gebesa Category',
    )

    quantity = fields.Float()

    std_cost = fields.Float()

    total_cost = fields.Float()
    total_consume_cost = fields.Float()

    monthly_qty_consume = fields.Float()
    months_inventory = fields.Float()

    uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Product UoM'
    )

    default_code = fields.Char('Internal Reference',)

    product_origin = fields.Char('Origin',)

    rawmat_rotation = fields.Char('Rotation',)
