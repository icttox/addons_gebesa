# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class TmsTirePositionHist(models.Model):
    _name = 'tms.tire.position.hist'
    _order = 'date desc'
    _description = 'descripcion pendiente'

    unit_old_id = fields.Many2one(
        'fleet.vehicle',
        string='Unit Old',
    )

    unit_new_id = fields.Many2one(
        'fleet.vehicle',
        string='Unit New',
    )

    position_old = fields.Integer(
        string='Position Old',
    )

    position_new = fields.Integer(
        string='Position New',
    )

    odometer_old = fields.Integer(
        string='Odometer Old',
    )

    odometer_new = fields.Integer(
        string='Odometer New',
    )

    tire_id = fields.Many2one(
        'tires',
        string='Tires',
        required=True,
    )

    date = fields.Date(
        string="Date"
    )
