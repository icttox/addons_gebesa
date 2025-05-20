# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import os
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.immex_gebesa.models import util


class CfdiFiel(models.Model):
    _name = 'cfdi.fiel'
    _rec_name = 'serial_number'
    _description = 'descripcion pendiente'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        help='Company where you add this fiel',
        default=lambda self: self.env.user.company_id.id,
    )

    fiel_file = fields.Binary(
        string='fiel File',
        help='This file .cer is proportionate by the SAT',
        filters='*.cer,*.certificate,*.cert',
    )

    fiel_key_file = fields.Binary(
        string='fiel Key File',
        help='This file .key is proportionate by the SAT',
        filters='*.key',
    )

    fiel_password = fields.Char(
        string='fiel Password',
        help='This password is proportionate by the SAT',
        size=64,
    )

    fiel_file_pem = fields.Binary(
        compute='_get_fiel_info',
        store=True,
        string='Fiel File PEM',
        help='This file is generated with the file.cer',
        filters='*.pem,*.cer,*.certificate,*.cert',
    )

    fiel_key_file_pem = fields.Binary(
        compute='_get_fiel_info',
        store=True,
        string='fiel Key File PEM',
        help='This file is generated with the file.key',
        filters='*.pem,*.key',
    )

    date_start = fields.Date(
        compute='_get_fiel_info',
        store=True,
        string='Date Start',
        help='Date start the fiel before the SAT',
        default=fields.Date.today,
    )

    date_end = fields.Date(
        compute='_get_fiel_info',
        store=True,
        string='Date End',
        help='Date end of validity of the fiel',
    )

    serial_number = fields.Char(
        compute='_get_fiel_info',
        store=True,
        string='Serial Number',
        size=64,
        help='Number of serie of the fiel',
    )

    fname_xslt = fields.Char(
        string='File XML Parser (.xslt)',
        size=256,
        help='Folder in server with XSLT file',
    )
    active = fields.Boolean(
        string='Active',
        help='Indicate if this fiel is active',
        default=True
    )

    @api.depends('fiel_file', 'fiel_key_file',
                 'fiel_password')
    def _get_fiel_info(self):
        cer_der_b64str = self.fiel_file
        key_der_b64str = self.fiel_key_file
        password = self.fiel_password
        data = self._resolve_fiel_info(
            cer_der_b64str, key_der_b64str, password)
        if data['warning']:
            raise ValidationError(data['warning']['message'])
        if data['value']:
            self.date_start = data['value']['date_start']
            self.date_end = data['value']['date_end']
            self.fiel_file_pem = data['value']['fiel_file_pem']
            self.fiel_key_file_pem = data[
                'value']['fiel_key_file_pem']
            self.serial_number = data['value']['serial_number']

    @api.model
    def _resolve_fiel_info(self, cer_der_b64str=None,
                           key_der_b64str=None, password=None):
        """
        @param cer_der_b64str : File .cer in Base 64
        @param key_der_b64str : File .key in Base 64
        @param password : Password inserted in the certificate configuration
        """
        value = {}
        warning = {}
        if cer_der_b64str and key_der_b64str and password:
            fname_cer_der = cer_der_b64str
            fname_key_der = util.b64str_to_tempfile(
                key_der_b64str, file_suffix='.der.key',
                file_prefix='openerp__' + (False or '') + '__ssl__')
            password = password.encode("utf-8")
            fname_password = util.b64str_to_tempfile(
                base64.b64encode(password),
                file_suffix='der.txt',
                file_prefix='openerp__' + (False or '') + '__ssl__',)
            cer_pem = util._transform_der_to_pem(
                fname_cer_der, type_der='cer')
            cer_pem_b64 = base64.encodebytes(cer_pem)

            key_pem = util._transform_der_to_pem(
                key_der_b64str, password, type_der='key')

            key_pem_b64 = base64.encodebytes(key_pem)

            date_fmt_return = '%Y-%m-%d'
            serial = False
            try:
                serial = util._get_param_serial(
                    cer_pem_b64, types='DER')
                value.update({
                    'serial_number': serial,
                })
            except BaseException:
                pass
            date_start = False
            date_end = False
            try:
                dates = util._get_param_dates(
                    cer_pem_b64, date_fmt_return=date_fmt_return)
                date_start = dates.get('startdate', False)
                date_end = dates.get('enddate', False)
                value.update({
                    'date_start': date_start,
                    'date_end': date_end,
                })

            except BaseException:
                pass
            os.unlink(fname_key_der)
            os.unlink(fname_password)

            if not key_pem_b64 or not cer_pem_b64:
                warning = {
                    'title': _('Warning!'),
                    'message': _(
                        'You fiel file, key file or password '
                        'is incorrect.\nVerify uppercase and lowercase')
                }
                value.update({
                    'fiel_file_pem': False,
                    'fiel_key_file_pem': False,
                })
            else:
                value.update({
                    'fiel_file_pem': cer_pem_b64,
                    'fiel_key_file_pem': key_pem_b64,
                })
        return {'value': value, 'warning': warning}
