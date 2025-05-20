# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    gps_history_ids = fields.One2many(
        'position.gps.history',
        'vehicle_id',
        string='Gps history',
    )

    @api.multi
    def gps_wsa_scanner(self):
        gps_history_obj = self.env['position.gps.history']
        res = super(FleetVehicle, self).gps_wsa_scanner()
        trucks_wimei = self.search([('imei', '!=', False)])
        for truck in trucks_wimei:
            gps_history_obj.create({
                'datetime': fields.Datetime.now(),
                'latitude': truck.latitude,
                'longitude': truck.longitude,
                'vehicle_id': truck.id
            })
        return res
