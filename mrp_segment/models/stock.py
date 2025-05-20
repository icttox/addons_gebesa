# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    related_segment = fields.Char(
        string='Relatad Segment',
        default='',
    )


class StockMove(models.Model):
    _inherit = 'stock.move'

    related_segment = fields.Char(
        string='Relatad Segment',
        default='',
    )

    @api.multi
    def _action_cancel(self):
        result = super(StockMove, self)._action_cancel()
        for move in self:
            if move.production_id and move.production_id.segment_line_ids:
                production = move.production_id
                manufacture_qty = 0
                for move_create in production.finished_move_line_ids.filtered(lambda l: l.state == 'cancel'):
                    manufacture_qty += move_create.product_uom_qty
                production.segment_line_ids.manufacture_qty += manufacture_qty
        return result

    @api.multi
    def _action_done(self):
        result = super(StockMove, self)._action_done()
        # procurement_obj = self.env['procurement.order']
        segments = []
        for move in self:
            if move.production_id and move.production_id.segment_line_ids:
                production = move.production_id
                manufacture_qty = 0
                # move_finished_ids
                for move_create in production.move_finished_ids.filtered(lambda l: l.state != 'done'):
                    manufacture_qty += move_create.product_uom_qty
                production.segment_line_ids.manufacture_qty = manufacture_qty
                # production.segment_line_ids.quantity = manufacture_qty
                product_qty = production.segment_line_ids.product_qty

                if manufacture_qty == 0:
                    segment = production.segment_line_ids.segment_id
                    if segment not in segments:
                        segments.append(segment)

                move_dest = move.mapped('move_dest_ids').mapped('move_dest_ids')
                if move.sale_line_id:
                    if move_dest:
                        if all(x for x in move_dest if x.location_dest_id.usage == 'customer'):
                            product = move.sale_line_id.product_id
                            if product.id == move_dest[0].product_id.id:
                                move.sale_line_id.write({
                                    'segment_qty': product_qty - manufacture_qty})

                # procurement = procurement_obj.search([
                #     ('production_id', '=', production.id)])
                # group = procurement.group_id
                # move_dest = procurement.move_dest_id.move_dest_id
                # procurement2 = procurement_obj.search([
                #     ('group_id', '=', group.id),
                #     ('product_id', '=', production.product_id.id),
                #     ('sale_line_id', '!=', False),
                #     ('move_ids', '=', move_dest.id)])
                # if procurement2:
                #     procurement2.sale_line_id.write(
                #         {'segment_qty': product_qty - manufacture_qty})

        for seg in segments:
            seg.action_done()
        return result
