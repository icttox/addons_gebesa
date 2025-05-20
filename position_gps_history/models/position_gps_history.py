# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons.base_geoengine import fields as geo_fields


# class PositionGpsHistory(geo_model.GeoModel):
class PositionGpsHistory(models.Model):
    _name = 'position.gps.history'
    _rec_name = 'datetime'
    _description = 'descripcion pendiente'

    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle',
    )
    datetime = fields.Datetime(
        string='Date',
    )
    latitude = fields.Float(
        string='Latitude',
        required=False, digits=(20, 10),
        help='GPS Latitude'
    )
    longitude = fields.Float(
        string='Longitude',
        required=False, digits=(20, 10),
        help='GPS Longitude'
    )
    point = geo_fields.GeoPoint(
        string='Coordinate',
        compute='_compute_point'
    )

    @api.depends('latitude', 'longitude')
    def _compute_point(self):
        for rec in self:
            rec.point = geo_fields.GeoPoint.from_latlon(
                self.env.cr, rec.latitude, rec.longitude)
