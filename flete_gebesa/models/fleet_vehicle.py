# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from xml.dom.minidom import parseString
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base_geoengine import fields as geo_fields
from dateutil.relativedelta import relativedelta
import requests


# class FleetVehicle(geo_model.GeoModel):
class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    performance = fields.Float(
        string='Performance',
    )

    axis = fields.Integer(
        string='Axis',
    )

    load_capacity = fields.Char(
        string='Drag Load Capacity',
    )

    tank = fields.Integer(
        string='Tank',
    )

    suspension = fields.Selection(
        [('air', 'Air'),
         ('pneumatics', 'Pneumatics'),
         ('springs', 'Springs')],
        string='Suspension'
    )

    cubic_mtr = fields.Float(
        string='Cubic Meters',
    )

    feet = fields.Float(
        string='Feets',
    )

    type_box = fields.Selection(
        [('dry_48', '48 Ft Dry Box'),
         ('dry_53', '53 Ft Dry Box'),
         ('platform_40_2', 'Platform 40 Ft 2 Axles'),
         ('platform_40_3', 'Platform 40 Ft 3 Axles'),
         ('thermo_48', 'Thermo 48 Ft'),
         ('thermo_53', 'Thermo 53 Ft')],
        string='Trailer Type'
    )

    tires_id = fields.One2many(
        'tires',
        'fleet_vehicle_id',
        string='Tire'
    )

    vehicle_event_id = fields.One2many(
        'fleet.vehicle.event',
        'vehicle_id',
        string='Event'
    )

    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
    )

    imei = fields.Char(
        string='Imei',
    )

    metas = fields.Float(
        string='Goal',
    )

    meta_mensual = fields.Float(
        string='Meta Mensual',
    )

    meta_diaria = fields.Float(
        string='Meta Diaria',
    )

    incentivo = fields.Float(
        string='Incentivo',
    )

    ##### Geo Position
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

    status = fields.Selection(
        [('active', 'En Viaje'),
         ('lack_driver', 'Parado Falta Chofer'),
         ('stopped_workshop', 'Parado Por Taller'),
         ('lack_sales', 'Parado Falta Ventas'),
         ('to_leave', 'Por Salir'),
         ('to_arrive', 'Por Llegar')],
        string='Estatus',
        default='lack_sales'
    )

    categories_trucks = fields.Selection(
        [('big', 'Grandes'),
         ('sterlin', 'Sterlin'),
         ('transformed', 'Transformados'),
         ('old', 'Viejos'),
         ('four_tons', '4 Toneladas')],
        string='Categoria Camión',
        default='big'
    )

    @api.constrains('tires_id', 'fleet_type')
    def _check_tires_id(self):
        for vehicle in self:
            tires = False
            if vehicle.fleet_type == 'tractor':
                tires = 10
            if vehicle.fleet_type in ('trailer', 'dolly'):
                tires = 8
            if tires:
                if tires < len(vehicle.tires_id):
                    raise ValidationError(
                        "The vehicle can only have a maximum of %s tires" % (
                            tires))

    @api.multi
    def gps_wsa_scanner(self):
        for vehicle in self:
            if not vehicle.imei:
                raise UserError(_(
                    'This truck %s has not a valid imei number') % (vehicle.name))
            db = u'https://67.219.149.214:9003/ws'
            xml = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:tem="http://tempuri.org/">
               <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                 <wsa:Action>http://tempuri.org/IGpsWebServices/GetReportLastMessage</wsa:Action>
                 <wsa:To>https://67.219.149.214:9003/ws</wsa:To>
               </soap:Header>
               <soap:Body>
                  <tem:GetReportLastMessage>
                     <tem:userName>tgalbo</tem:userName>
                     <tem:userPassword>PROVERBIOS</tem:userPassword>
                  </tem:GetReportLastMessage>
               </soap:Body>
            </soap:Envelope>"""
            headers = {
                'Content-Type': 'application/soap+xml; charset=utf-8',
            }
            try:
                req = requests.request(
                    'POST', db, data=xml,
                    headers=headers, verify=False)
            except BaseException as e:
                raise UserError(_(
                    'Error al conectarse con GPS'
                    'Error: %s.') % (e))
            resultados_mensaje = req.content
            dom = parseString(resultados_mensaje)

            rows = dom.getElementsByTagName(
                'b:ReportLastMessageRow')

            trucks_wimei = self.env['fleet.vehicle'].search([('imei', '!=', False)])
            for row in rows:
                row_imei = row.getElementsByTagName('b:imei')
                row_imei = row_imei[0].firstChild.nodeValue
                lat = row.getElementsByTagName('b:latitude')
                lat = lat[0].firstChild.nodeValue
                lon = row.getElementsByTagName('b:longitude')
                lon = lon[0].firstChild.nodeValue

                for truck in trucks_wimei:
                    if truck.imei == row_imei:
                        truck.latitude = lat
                        truck.longitude = lon
                # if row_imei != self.imei:
                #     continue
        return True

    @api.depends('latitude', 'longitude')
    def _compute_point(self):
        for rec in self:
            rec.point = geo_fields.GeoPoint.from_latlon(
                self.env.cr, rec.latitude, rec.longitude)

    @api.multi
    def open_in_google(self):
        for truck in self:
            url = ("/tms/static/src/googlemaps/get_place_from_coords.html?" +
                   str(truck.latitude) + ',' + str(truck.longitude))
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'nodestroy': True,
            'target': 'new'}

    @api.model
    def check_position_trailer(self):
        vehicle_obj = self.env['fleet.vehicle'].search([
            ('active', '=', True),
            ('fleet_type', '=', 'tractor'),
            ('imei', '!=', False)], limit=1)

        vehicle_obj.gps_wsa_scanner()
        return True

    # @api.onchange('fleet_type')
    # def count_tires(self):
    #    pos1 = self.pos1_tires_id
    #    pos10 = self.pos10_tires_id
    #    diez_llantas = [pos1, pos2, pos3, pos4, pos8, pos7, pos6, pos5, pos9, pos10]
    #    ocho_llantas = [pos1, pos2, pos3, pos4, pos8, pos7, pos6, pos5]

    #    if self.fleet_type == 'tractor':
    #        return(diez_llantas)

    #    if self.fleet_type == 'trailer' or self.fleet_type == 'dolly':
    #        return(ocho_llantas)

    @api.model
    def call_gps_wsa_scanner(self):

        vehicles = self.search([
            ('imei', '!=', None)])
        vehicles.gps_wsa_scanner()

    @api.model
    def delete_history_gps(self):
        vehicles_dt_obj = self.env['position.gps.history']
        vehicles_dt = vehicles_dt_obj.search([
            ('datetime', '!=', None)])
        total = datetime.today() + relativedelta(months=-3)
        for x in vehicles_dt:
            limit_date = x.datetime
            date_time_obj = fields.Datetime.from_string(limit_date)
            if date_time_obj <= total:
                x.unlink()
