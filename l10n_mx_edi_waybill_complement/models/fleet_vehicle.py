# -*- coding: utf-8 -*-

from odoo import api, models, fields


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    conf_vehicle = fields.Many2one(
        'l10n.mx.wbl.autotransport.conf',
        string='Autotransport Configuration',
    )

    sub_type_rem = fields.Many2one(
        'l10n.mx.wbl.trailer.type',
        string='Trailer Type',
    )

    carry_trailer = fields.Selection(
        related='conf_vehicle.carry_trailer',
        string='Trailer'
    )

    trailer = fields.Boolean(
        string='Trailer',
    )

    @api.onchange('conf_vehicle')
    def onchange_conf_vehicle(self):
        if self.conf_vehicle.carry_trailer == 'carries':
            self.trailer = True
        else:
            self.trailer = False
