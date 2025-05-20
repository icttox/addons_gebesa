# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # def force_transfer(self, force_qty=True):
    #     for pick in self:
    #         for pack in pick.pack_operation_ids:
    #             if not pack.qty_done > 0:
    #                 pack.unlink()
    #         pick.do_transfer()
