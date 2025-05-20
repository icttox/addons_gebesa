# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import base64
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle',
    )
    route_id = fields.Many2one(
        'tms.route',
        string='Route',
    )
    travel_ids = fields.Many2many(
        'tms.travel',
        string='Travels',
    )
    full_tank = fields.Boolean(
        string='Full tank',
    )
    driver_id = fields.Many2one(
        'hr.employee',
        string='Driver',
    )
    kilometer = fields.Float(
        string='kilometer',
    )
    image_qr = fields.Binary(
        attachment=True,
        string="File QR")

    fecha_despacho = fields.Datetime(
        string='Fecha de despacho'
    )

    @api.multi
    def action_done(self):
        ctx = self._context.copy()
        for picking in self:
            if self.env.user.has_group('tms.group_expenses') or \
                    self.env.user.has_group('tms.group_monitoring') or \
                    self.env.user.has_group('tms.group_supervisor_traffic') or \
                    self.env.user.has_group('tms.group_traffic'):
                if picking.location_dest_id.usage == 'inventory' and not picking.vehicle_id:
                    raise ValidationError(_(
                        "El picking %s no tiene asignado un vehiculo") % (
                        picking.name))
            if picking.vehicle_id:
                ctx.update({
                    'force_vehicle_analytic_id': picking.vehicle_id.account_analytic_id.id})
        return super().action_done()

    @api.multi
    def generate_qr(self):
        report_obj = self.env['report']

        str_qr = self.env['ir.config_parameter'].get_param('web.base.url')
        str_qr += '/web#id=%s&view_type=form&model=stock.picking&action=241\
            &menu_id=178' % str(self.id)

        qr = report_obj.barcode(
            barcode_type='QR', value=str_qr, width=500, height=500)
        self.image_qr = base64.encodestring(qr)

        file_name = self.name.replace("/", "-")

        return {
            'type': 'ir.actions.act_url',
            'url': self.get_compose_download_qr_url(
                file_name + '.png'),
            'target': 'new',
        }

    def get_compose_download_qr_url(self, filename, download=True):
        base_url = ("/web/content/{model}/{res_id}/image_qr/{filename}"
                    "?download={download}")
        return base_url.format(
            model=self._name, res_id=self.id, filename=filename,
            download=json.dumps(download))
