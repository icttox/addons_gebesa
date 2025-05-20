# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class TmsRoute(models.Model):
    _inherit = 'tms.route'
    _name = 'tms.route'

    three_tons = fields.Float(
        string='3 Tons: ',)

    normal_box = fields.Float(
        string='Normal Box: ',
    )

    pupies = fields.Float(
        string='Pupies: ',
    )

    combo = fields.Float(
        string='Combo: ',)

    # relacion para hacer un one2many
    # shipment_id = fields.Many2one(
    #    'mrp.shipment',
    #    string=_('Shipment'),)
