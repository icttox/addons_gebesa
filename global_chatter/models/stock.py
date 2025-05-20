# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['message.post.show.all', 'stock.picking']


# class StockBatchPicking(models.Model):
#     _name = 'stock.batch.picking'
#     _inherit = ['stock.batch.picking', 'message.post.show.all']


# class StockWarehouse(models.Model):
#     _name = 'stock.warehouse'
#     _inherit = ['stock.warehouse', 'message.post.show.all']


class StockLocation(models.Model):
    _name = 'stock.location'
    _inherit = ['message.post.show.all', 'stock.location']


class StockPickingType(models.Model):
    _name = 'stock.picking.type'
    _inherit = ['message.post.show.all', 'stock.picking.type']
