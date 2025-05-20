# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo import models


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    def action_done(self):
        self.action_check()
        self.write({'state': 'done'})
        self.post_inventory()
        return True
