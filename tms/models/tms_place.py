# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import requests
import simplejson as json

from odoo import api, fields, models
from odoo.addons.base_geoengine import fields as geo_fields
from odoo.exceptions import UserError
from odoo.tools.translate import _


# class TmsPlace(geo_model.GeoModel):
class TmsPlace(models.Model):
    _name = 'tms.place'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Cities / Places'

    name = fields.Char('Place', size=64, required=True, index=True)
    complete_name = fields.Char(compute='_compute_complete_name')
    state_id = fields.Many2one(
        'res.country.state',
        string='State Name')
    country_id = fields.Many2one(
        'res.country',
        related='state_id.country_id',
        string='Country')
    latitude = fields.Float(
        required=False, digits=(20, 10),
        help='GPS Latitude')
    longitude = fields.Float(
        required=False, digits=(20, 10),
        help='GPS Longitude')
    point = geo_fields.GeoPoint(
        string='Coordinate',
        store=True,
        compute='_compute_point'
    )

    @api.multi
    def get_coordinates(self):
        for rec in self:
            address = (rec.name + "," + rec.state_id.name + "," +
                       rec.country_id.name)
            google_url = (
                'https://maps.googleapis.com/maps/api/geocode/json?' +
                'address=' + str(address.encode('utf-8'))[2:-1] +
                '&sensor=false' +
                '&key=AIzaSyCKBWo-QHHefkWfPZaPjAJT9HDtpY307KI')
            try:
                result = json.loads(requests.get(google_url).content)
                if result['status'] == 'OK':
                    location = result['results'][0]['geometry']['location']
                    self.latitude = location['lat']
                    self.longitude = location['lng']
                else:
                    errmsj = result['error_message']
                    message_body = "<b>%s:</b> %s" % (
                        _("El servicio de googlemaps regresó el siguiente error: "), errmsj)
                    self.message_post(body=message_body)
            except:
                raise UserError(_("Google Maps is temporary unavailable."))

    @api.multi
    def open_in_google(self):
        for place in self:
            url = ("/tms/static/src/googlemaps/get_place_from_coords.html?" +
                   str(place.latitude) + ',' + str(place.longitude))
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'nodestroy': True,
            'target': 'new'}

    @api.depends('name', 'state_id')
    def _compute_complete_name(self):
        for rec in self:
            if rec.state_id:
                rec.complete_name = rec.name + ', ' + rec.state_id.name
            else:
                rec.complete_name = rec.name

    @api.depends('latitude', 'longitude')
    def _compute_point(self):
        for rec in self:
            rec.point = geo_fields.GeoPoint.from_latlon(
                self.env.cr, rec.latitude, rec.longitude)
