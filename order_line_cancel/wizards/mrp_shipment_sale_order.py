# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class MrpShipmentSaleOrder(models.TransientModel):
    _inherit = 'mrp.shipment.sale.order'

    @api.multi
    def _check_order_line_closed(self, line):
        if line.closed is True:
            return True
        return False
