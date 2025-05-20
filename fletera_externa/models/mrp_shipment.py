# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
# from odoo.exceptions import ValidationError


class MrpShipment(models.Model):
    _inherit = 'mrp.shipment'

    operator = fields.Char(
        string='Operator',
    )

    truck = fields.Char(
        string='Truck',
    )

    deliveries = fields.Integer(
        string='Deliveries',
    )

    plaque = fields.Char(
        string='Plaque',
    )

    order = fields.Integer(
        string='Order',
    )

    importe = fields.Integer(
        string='Amount',
    )

    cobranza = fields.Char(
        string='Ins. de Cobranza',
    )

    instruction = fields.Char(
        string='Instruction',
    )
