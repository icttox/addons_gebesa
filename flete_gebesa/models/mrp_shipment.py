# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
# from odoo.exceptions import ValidationError


class MrpShipment(models.Model):
    _inherit = 'mrp.shipment'

    route_ids = fields.Many2one(
        'tms.route',
        string='Routes',
        copy=False
    )

    type_route = fields.Selection(
        [('normal_box', 'Normal Box'),
         ('three_tons', '3 Tons'),
         ('pupies', 'Pupies'),
         ('combo', 'Combo')],
        string='Type route',
        copy=False
    )

    linea_partner = fields.Char(
        string='Customers',
        compute="_compute_extra_dat",
    )
    linea_citys = fields.Char(
        string='Citys',
        compute="_compute_extra_citys",
    )

    @api.depends('line_ids')
    def _compute_extra_dat(self):
        for ship in self:
            partner_name = ''
            if ship.line_ids:
                for name in ship.line_ids.mapped('partner_id').mapped('name'):
                    partner_name += name + ', '
                partner_name = partner_name[:-2]
            ship.linea_partner = partner_name

    @api.depends('line_ids')
    def _compute_extra_citys(self):
        for ship in self:
            city_name = ''
            city = []
            if ship.line_ids:
                for name in ship.line_ids.mapped('city'):
                    if name not in city:
                        city.append(name)
                        city_name += name + ', '
                city_name = city_name[:-2]
            ship.linea_citys = city_name
