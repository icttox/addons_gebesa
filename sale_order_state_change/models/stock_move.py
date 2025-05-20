# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import models

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    # INCOMPLETO
    # @api.multi
    # def procurement_searh(self):
    #     proc_obj = self.env['procurement.order']
    #     import ipdb; ipdb.set_trace()
    #     if self.state not in ['cancel', 'done']:
    #         self.do_unreserve()
    #         self.env.cr.execute("""UPDATE stock_move SET state = 'cancel'
    #                               WHERE id in (%s) """ % (self.id))
    #     procurement = proc_obj.search([('move_dest_id', '=', self.id)])
    #     if procurement.state in ['confirmed', 'exception', 'running']:
    #                 self.env.cr.execute("""UPDATE procurement_order SET state = 'cancel'
    #                                 WHERE id = %s """ % (procurement.id))
    #     moves = self.search([('procurement_id', '=', procurement.id)])
    #     for move in moves:
    #         _logger.error("stock.move" + str(move.id))
    #         procurement_1 = proc_obj.search([('move_dest_id', '=', move.id)])
    #         if procurement_1.state in ['confirmed', 'exception', 'running']:
    #                 self.env.cr.execute("""UPDATE procurement_order SET state = 'cancel'
    #                                 WHERE id = %s """ % (procurement_1.id))
    #         if procurement_1.purchase_line_id:
    #             continue
    #         production = procurement_1.production_id
    #         if production:
    #             if production.move_prod_id.state not in ['cancel', 'done']:
    #                 production.move_prod_id.do_unreserve()
    #                 _logger.error("stock.move" + str(production.move_prod_id.id))
    #                 self.env.cr.execute("""UPDATE stock_move SET state = 'cancel'
    #                                 WHERE id in (%s) """ % (production.move_prod_id.id))
    #             for mov in production.move_created_ids:
    #                 _logger.error("stock.move" + str(mov.id))
    #                 if mov.state not in ['cancel', 'done']:
    #                     mov.do_unreserve()
    #                     self.env.cr.execute("""UPDATE stock_move SET state = 'cancel'
    #                                 WHERE id in (%s) """ % (mov.id))
    #             for line in production.move_lines:
    #                 _logger.error("stock.move" + str(line.id))
    #                 if line.state not in ['cancel', 'done']:
    #                     line.do_unreserve()
    #                     self.env.cr.execute("""UPDATE stock_move SET state = 'cancel'
    #                                 WHERE id in (%s) """ % (line.id))
    #             for picking in production.picking_raw_material_ids:
    #                 for move_picking in picking.move_lines:
    #                     move_picking.procurement_searh()
    #                 if picking.state in ['draft', 'waiting', 'confirmed']:
    #                     self.env.cr.execute("""UPDATE stock_picking SET state = 'cancel'
    #                                 WHERE id in (%s) """ % (picking.id))
    #             if production.state in ['draft', 'confirmed', 'ready']:
    #                 self.env.cr.execute("""UPDATE mrp_production SET state = 'cancel'
    #                                 WHERE id = %s """ % (production.id))

    #     return True
