# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import api, fields, models
# from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # quant_recalculated = fields.Boolean(
    #     string='Quant recalculated',
    #     default=False,
    # )

    @api.multi
    def product_fix_reserved_qty(self):
        self._cr.execute("""
            UPDATE stock_quant sq SET reserved_quantity = COALESCE(datas.reserved_quantity_new, 0.00)
            FROM (
                SELECT
                    sl.name,
                    pp.default_code,
                    sq.id AS sq_id,
                    SUM(sml.product_qty) AS reserved_quantity_new,
                    sq.reserved_quantity,
                    sq.quantity
                FROM stock_move_line AS sml
                JOIN stock_location AS sl ON sml.location_id = sl.id
                JOIN product_product AS pp ON sml.product_id = pp.id
                JOIN stock_quant AS sq ON sml.location_id = sq.location_id AND sml.product_id = sq.product_id
                WHERE sml.product_qty > 0
                    AND sl.usage IN ('internal')
                    AND sl.active IS TRUE
                    AND sl.company_id = %s
                GROUP BY sl.id, pp.id, sq.id
                HAVING ROUND(SUM(sml.product_qty), 6) != ROUND(CAST(sq.reserved_quantity AS NUMERIC), 6)) AS datas
            WHERE sq.id = datas.sq_id""" % (self.env.user.company_id.id))

    @api.model
    def product_quant_recalculated_auto(self):
        # Marca error al intentar deshacer la reserva por que
        # la cantidad reservada algunas veces está descuadrada
        self.product_fix_reserved_qty()

        locations = self.env['stock.location'].search([
            ('usage', '=', 'internal'),
            ('active', '=', True),
            ('company_id', '=', self.env.user.company_id.id)])

        for loc in locations:
            self._cr.execute("""
                SELECT
                    *
                FROM (
                    SELECT
                        pp.id AS product_id,
                        pp.default_code AS codigo,
                        pp.name_template AS producto,
                        COALESCE(ROUND(CAST(SUM(CASE
                            WHEN sm.location_id = sm.location_dest_id THEN 0
                            WHEN sm.location_dest_id = %s THEN sm.product_qty
                            ELSE sm.product_qty * -1 END) AS NUMERIC), 6), 0.000000) AS existencia,
                        COALESCE(ROUND(CAST((SELECT
                            SUM(quantity)
                        FROM stock_quant
                        WHERE product_id = pp.id
                            AND location_id = %s) AS NUMERIC), 6), 0.000000) AS existencia_quant
                    FROM product_product pp
                    JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                    JOIN stock_move sm on pp.id = sm.product_id
                    WHERE (sm.location_dest_id = %s OR sm.location_id = %s)
                        AND pt.type = 'product'
                        AND sm.state = 'done'
                        AND sm.company_id = %s
                    GROUP BY pp.id) AS datas
                WHERE existencia != existencia_quant""", (
                loc.id, loc.id, loc.id, loc.id, loc.company_id.id))
            for prod in self._cr.fetchall():
                product_id = prod[0]
                move_ids = self.env['stock.move'].search([
                    ('state', 'in', ['partially_available', 'assigned']),
                    ('location_id', '=', loc.id),
                    ('product_id', '=', product_id)])

                # Marca error al intentar deshacer la reserva por que
                # la cantidad reservada algunas veces está descuadrada
                # self._cr.execute("""
                #     UPDATE stock_quant sq SET reserved_quantity = COALESCE(datas.reserved_quantity, 0.00)
                #     FROM (
                #         SELECT SUM(sml.product_qty) AS reserved_quantity, sml.location_id, sml.product_id
                #         FROM stock_move_line sml WHERE sml.location_id = %s
                #             AND sml.product_id = %s AND sml.product_qty > 0
                #         GROUP BY sml.location_id, sml.product_id) AS datas
                #     WHERE sq.location_id = datas.location_id and sq.product_id = datas.product_id
                #     """, ([loc.id, product_id]))

                move_ids._do_unreserve()

                quant_ids = self.env['stock.quant'].search([
                    ('location_id', '=', loc.id),
                    ('product_id', '=', product_id)])
                quant_ids.with_context({'force_unlink': True}).unlink()

                self._cr.execute(
                    """
                        SELECT
                            product_id,
                            COALESCE(
                                ROUND(SUM(product_qty * CASE
                                    WHEN location_id = location_dest_id THEN 0
                                    WHEN location_dest_id = %s THEN 1
                                    ELSE -1 END), 6
                                ),0.00
                            )
                        FROM stock_move
                        WHERE (location_id = %s OR location_dest_id = %s)
                            AND company_id = %s
                            AND product_id = %s
                            AND state = 'done'
                        GROUP BY product_id
                    """, ([
                        loc.id, loc.id, loc.id, loc.company_id.id, product_id]))
                for quant in self._cr.fetchall():
                    if quant[1] != 0.00:
                        self.env['stock.quant'].create({
                            'product_id': quant[0],
                            'location_id': loc.id,
                            'quantity': quant[1],
                            'in_date': fields.Datetime.now(),
                        })
                        _logger.info(
                            'Quant corregiduo ubicacion %s producto %s', loc.name, prod[1])

    @api.model
    def product_quant_recalculated(self, to_locations=False):
        quant_obj = self.env['stock.quant']
        move_obj = self.env['stock.move']
        location_obj = self.env['stock.location']
        if to_locations:
            locations = location_obj.search([
                ('usage', 'not in', ['view']),
                ('id', 'in', to_locations)])
        else:
            locations = location_obj.search([('usage', 'not in', ['view'])])

        for location in locations:
            move_ids = move_obj.search([
                ('state', 'in', ['partially_available', 'assigned']),
                ('location_id', '=', location.id)])

            # Marca error al intentar deshacer la reserva por que
            # la cantidad reservada algunas veces está descuadrada
            product_ids = move_ids.mapped('product_id')
            for product in product_ids:
                self._cr.execute(
                    """
                        SELECT sum(sml.product_qty) FROM stock_move_line sml
                        WHERE sml.location_id = %s and sml.product_id = %s
                        AND sml.product_qty > 0 GROUP BY sml.product_id
                    """, ([location.id, product.id]))

                qty_reser = self._cr.fetchall()

                if qty_reser:
                    qty_reser = qty_reser[0]
                else:
                    qty_reser = 0

                self._cr.execute(
                    """
                        UPDATE stock_quant sq SET reserved_quantity = %s
                        WHERE sq.location_id = %s and sq.product_id = %s
                    """, ([qty_reser, location.id, product.id]))

            move_ids._do_unreserve()

            quant_ids = quant_obj.search([('location_id', '=', location.id)])
            quant_ids.with_context({'force_unlink': True}).unlink()

            self._cr.execute(
                """
                    SELECT
                        product_id,
                        COALESCE(
                            ROUND(SUM(product_qty * CASE
                                WHEN location_id = location_dest_id THEN 0
                                WHEN location_dest_id = %s THEN 1
                                ELSE -1 END), 6
                            ),0.00
                        )
                    FROM stock_move
                    WHERE (location_id = %s OR location_dest_id = %s)
                        AND company_id = %s
                        AND state = 'done'
                    GROUP BY product_id
                """, ([location.id, location.id, location.id, location.company_id.id]))
            count = 0
            quants = self._cr.fetchall()
            for quant in quants:
                count += 1
                if quant[1] != 0.00:
                    quant_obj.create({
                        'product_id': quant[0],
                        'location_id': location.id,
                        'quantity': quant[1],
                        'in_date': fields.Datetime.now(),
                    })
                _logger.info(
                    'ubicacion %s quant %s de %s', location.name, count, len(quants))
        # self._cr.execute(
        #     """
        #         SELECT
        #             pp.id,
        #             COUNT(sm.id)
        #         FROM stock_move AS sm
        #         JOIN product_product AS pp ON pp.id = sm.product_id
        #         WHERE pp.quant_recalculated IS NOT TRUE
        #             AND sm.company_id = %s
        #             AND sm.state = 'done'
        #         GROUP BY pp.id
        #         ORDER BY COUNT(sm.id) desc
        #         LIMIT 100
        #     """, ([self.env.user.company_id.id]))
        # for product_id in self._cr.fetchall():
        #     quant_ids = quant_obj.search([('product_id', '=', product_id[0])])
        #     quant_ids.with_context({'force_unlink': True}).unlink()

        #     count = 0
        #     for move in move_ids:
        #         count += 1
        #         move_qty_cmp = float_compare(
        #             move.product_qty, 0,
        #             precision_rounding=move.product_id.uom_id.rounding)
        #         if move_qty_cmp > 0:
        #             main_domain = [('qty', '>', 0)]
        #             preferred_domain = [('reservation_id', '=', move.id)]
        #             fallback_domain = [('reservation_id', '=', False)]
        #             fallback_domain2 = ['&', ('reservation_id', '!=', move.id),
        #                                 ('reservation_id', '!=', False)]
        #             preferred_domain_list = [preferred_domain] + \
        #                 [fallback_domain] + [fallback_domain2]
        #             quants = quant_obj.quants_get_preferred_domain(
        #                 qty=move.product_qty, move=move, domain=main_domain,
        #                 preferred_domain_list=preferred_domain_list)
        #             quant_obj.quants_move(
        #                 quants=quants, move=move,
        #                 location_to=move.location_dest_id,
        #                 lot_id=move.restrict_lot_id.id,
        #                 owner_id=move.restrict_partner_id.id)
        #         _logger.info('%s de %s', count, len(move_ids))
        #         for quant in move.quant_ids:
        #             quant.write({'in_date': move.date})
        #     self.browse([product_id[0]]).write({
        #         'quant_recalculated': True})
