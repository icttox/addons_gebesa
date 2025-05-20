# -*- coding: utf-8 -*-
# Copyright 2021, Leslie Marquez.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import os
import datetime
import pytz
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class TmsTollImport(models.TransientModel):
    _name = 'tms.toll.wizard'
    _description = 'descripcion pendiente'

    filename = fields.Char(size=255)
    file = fields.Binary(
        string='Upload TollStation',
        required=True)

    @api.multi
    def update_tollstation_expense_gebesa(self):
        tollstation_obj = self.env['tms.travel.tollstation']
        vehicle_obj = self.env['fleet.vehicle']
        travel_obj = self.env['tms.travel']
        template_obj = self.env['product.template']
        template_var = template_obj.search([('tms_product_category', '=', 'tollstations'),
                                            ('active', '=', True)], limit=1)
        product_obj = self.env['product.product']
        product_var = product_obj.search([('product_tmpl_id', '=', template_var.id),
                                          ('active', '=', True)], limit=1)
        txt_extension = os.path.splitext(self.filename)[1].lower()
        tollstations_ids = []
        # if not self.env.user.default_operating_unit_id.id:
        #    raise ValidationError(_('The user %s have not operating unit') % (self.env.user.login))
        if txt_extension in ('.txt', '.dat'):
            try:
                document = base64.b64decode(self.file).decode('utf-8', 'replace')
                lines = document.split('\n')
                lines.remove('')
                for line in lines:
                    if (line == '\r' or
                            line[:10] == 'Operador,R'):
                        continue
                    split_line = line.split('"')
                    replace = False
                    line = ''
                    for sp_l in split_line:
                        if replace:
                            sp_l = sp_l.replace(',', '')
                        line += sp_l
                        replace = not replace

                    split_line = line.split(',')

                    arr_date = split_line[5].split("/")
                    str_time = split_line[6].replace('/', '-')
                    str_datetime = (arr_date[2] + '-' + arr_date[1] + '-' +
                                    arr_date[0] + ' ' + str_time)
                    fecha_cruze = datetime.datetime.strptime(
                        str_datetime, "%Y-%m-%d %H:%M:%S")
                    # import ipdb; ipdb.set_trace()
                    # fecha_cruze = pytz.timezone(
                    #     self._context.get('tz')).localize(
                    #     fecha_cruze, is_dst=False)
                    # fecha_cruze = fecha_cruze.astimezone(pytz.timezone('UTC'))
                    timezone = pytz.timezone(self._context.get('tz') or 'UTC')
                    fecha_cruze = pytz.UTC.localize(fecha_cruze)
                    fecha_cruze = fecha_cruze.astimezone(timezone)
                    fecha_cruze = fecha_cruze + relativedelta(hours=12.0)
                    fecha_cruze = fecha_cruze.strftime('%Y-%m-%d %H:%M:%S')

                    if not self.env.user.default_operating_unit_id.id:
                        raise ValidationError(_('You need a configuration Operating Unit'))
                    vehicle_var = False
                    vehicle_var = vehicle_obj.search([
                        ('tollstation_tag', '=', split_line[2]),
                        ('active', '=', True)],
                        limit=1)
                    travel_var = False
                    travel_var = travel_obj.search([
                        ('unit_id', '=', vehicle_var.id),
                        ('date_start_real', '<=', fecha_cruze),
                        ('date_end_real', '>=', fecha_cruze),
                        ('state', '!=', 'cancel')],
                        limit=1)
                    amount = split_line[12]
                    if amount in ('0.00', None):
                        amount = 0.01
                    toll = tollstation_obj.create({
                        'operador': split_line[0],
                        'red': split_line[1],
                        'tag': split_line[2],
                        'num_economico': split_line[3],
                        'category': split_line[4],
                        'fecha_cruze': fecha_cruze,
                        'num_plaza': split_line[7],
                        'nombre_plaza': split_line[8],
                        'tramo': split_line[9],
                        'carril': split_line[10],
                        'importe_total': abs(split_line[11]),
                        'amount': amount,
                        'operating_unit_id': self.env.user.default_operating_unit_id.id,
                        'product_id': product_var.id,  # 1614998,
                        'dictaminacion': split_line[14],
                        'id_pago': split_line[15],
                        'unit_id': vehicle_var.id,
                        'name': split_line[0] + ' - ' + split_line[8],
                        'travel_id': travel_var.id,
                        'employee_id': travel_var.employee_id.id, })
                    if not toll.unit_id:
                        if vehicle_var:
                            toll.write({'unit_id': vehicle_var.id})
                    if not toll.travel_id:
                        if travel_var:
                            toll.write({'travel_id': travel_var.id,
                                        'employee_id': travel_var.employee_id.id})
                    tollstations_ids.append(toll.id)

                return {
                    'name': 'TollStation Wizard',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'domain': [('id', 'in', tollstations_ids)],
                    'target': 'current',
                    'res_model': 'tms.travel.tollstation',
                    'type': 'ir.actions.act_window'
                }
            except Exception as message:
                raise ValidationError(_(
                    'Oops! Odoo has detected an error'
                    ' in the file. \nPlease contact your admin system.\n\n'
                    'Error message\n[' + str(message) + ']'))
        else:
            raise ValidationError(
                _('Oops! The files must have .txt or .dat extensions'))
