# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class MrpBom(models.Model):
    _name = 'mrp.bom'
    _inherit = ['message.post.show.all', 'mrp.bom']


class MrpBomLine(models.Model):
    _name = 'mrp.bom.line'
    _inherit = ['message.post.show.all', 'mrp.bom.line']


class MrpProduction(models.Model):
    _name = 'mrp.production'
    _inherit = ['message.post.show.all', 'mrp.production']


class MrpShipment(models.Model):
    _name = 'mrp.shipment'
    _inherit = ['message.post.show.all', 'mrp.shipment']
