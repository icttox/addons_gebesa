# -*- coding: utf-8 -*-
# Copyright 2021, Leslie Marquez.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import os
import datetime
# import pytz
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class TmsTollImportPase(models.TransientModel):
    _name = 'tms.toll.wizard.pase'
    _description = 'descripcion pendiente'

    filename = fields.Char(size=255)
    file = fields.Binary(
        string='Upload TollStation',
        required=True)

    @api.multi
    def update_tollstation_pase(self):
        template_var = self.env['product.template'].search([
            ('tms_product_category', '=', 'tollstations'),
            ('active', '=', True)], limit=1)
        product_var = self.env['product.product'].search([
            ('product_tmpl_id', '=', template_var.id),
            ('active', '=', True)], limit=1)
        tollstations_ids = []
        document = os.path.splitext(self.filename)[1].lower()

        if document in ('.txt', '.dat'):
            try:
                lines = base64.b64decode(self.file).decode(
                    'utf-8', 'replace').split('\n')
                lines.remove('')
                for line in lines:
                    if line[:10] == 'Tag|No.Eco':
                        continue
                    split_line = line.split('|')
                    time = split_line[3]
                    time_splite = time.split(':')
                    if len(time_splite) < 3:
                        time += ":00"
                    date = datetime.datetime.strptime(
                        split_line[2] + ' ' + time,
                        "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

                    if not self.env.user.default_operating_unit_id.id:
                        raise ValidationError(
                            _('You need a configuration Operating Unit'))
                    tag_line = split_line[0].replace('..', '')
                    vehicle_var = False
                    vehicle_var = self.env['fleet.vehicle'].search([
                        ('tollstation_tag', '=', tag_line),
                        ('active', '=', True)],
                        limit=1)
                    travel_var = False
                    travel_var = self.env['tms.travel'].search([
                        ('unit_id', '=', vehicle_var.id),
                        ('date_start_real', '<=', date),
                        ('date_end_real', '>=', date),
                        ('state', '!=', 'cancel')],
                        limit=1)
                    amount = split_line[7].replace(
                        '$', "").replace('-', "")
                    if amount == '0.00' or amount is None:
                        amount = 0.01
                    toll = self.env['tms.travel.tollstation'].create({
                        'tag': tag_line,
                        'num_economico': split_line[1],
                        'date': date,
                        'name': split_line[4],
                        'carril': split_line[5],
                        'category': split_line[6],
                        'importe_total': split_line[7].replace(
                            '$', "").replace('-', ""),
                        'amount': amount,
                        'operating_unit_id': self.env.user.default_operating_unit_id.id,
                        'product_id': product_var.id,  # 1614998,
                        'unit_id': vehicle_var.id,
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
                    'name': 'TollStation Wizard Pase',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'domain': [('id', 'in', tollstations_ids)],
                    'target': 'current',
                    'res_model': 'tms.travel.tollstation',
                    'type': 'ir.actions.act_window'
                }
            except Exception as message:
                raise ValidationError(_(
                    '¡Warning! Odoo has detected an error'
                    ' in the file. \nPlease contact your admin system.\n\n'
                    'Error message\n[' + str(message) + ']'))
        else:
            raise ValidationError(
                _('¡Error! The files must have .txt or .dat extensions'))
