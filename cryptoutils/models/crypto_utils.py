# -*- coding: utf-8 -*-
# Copyright 2019, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
import base64
import util
from settings import PATH
from odoo import api, fields, models
from odoo.exceptions import ValidationError

PEM_F = os.path.join(PATH['PEM'])
CER_F = os.path.join(PATH['CER'])
XML_F = os.path.join(PATH['XML'])
XSLT_F = os.path.join(os.path.dirname(__file__),
                      'cadena3.3.xslt')


class CryptoUtils(models.Model):
    _name = 'crypto.utils'
    _description = 'Modulo herramienta para manejo de openssl'

    def _get_certificate(self):
        res = {}
        for rec in self:
            # dict(self._context, date_work=invoice.date_invoice)
            certificate = False
            certificate = self.env['res.company'].browse(
                rec.company_id.id)._get_current_certificate()
            certificate_id = certificate[rec.company_id.id]
            res[rec.id] = certificate_id and certificate_id.id or False
        return res

    xml_string = fields.Text(
        string='XML String',
    )

    cadena_original = fields.Text(
        string='Cadena Original',
    )

    cadena_firmada = fields.Text(
        string='Cadena Firmada',
    )

    contenido_cer_pem = fields.Text(
        string='Cer Pem',
    )

    contenido_key_pem = fields.Text(
        string='Key Pem',
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'crypto.utils'),
    )

    @api.multi
    def genera_cadena_original(self):
        self.do_tmpfiles()
        for rec in self:
            rec.cadena_original = util.generate_cadena_original_fromstr(
                XSLT_F, self.xml_string)

    @api.multi
    def firma_cadena_original_sha256(self):
        self.do_tmpfiles()
        for rec in self:
            rec.cadena_firmada = util.get_sello_cadena_sha256(
                PEM_F, self.cadena_original)

    @api.multi
    def firma_cadena_original(self):
        self.do_tmpfiles()
        for rec in self:
            rec.cadena_firmada = util.get_sello_cadena(
                PEM_F, self.cadena_original)

    @api.multi
    def do_tmpfiles(self):
        """ Write tmp Cer file
        """
        for rec in self:
            certificate_id = self._get_certificate() or False

            if not certificate_id[rec.id]:
                raise ValidationError(
                    "There is not a valid Certificate (CSD)"
                    "for the company emmiter of this invoice,"
                    " verify please...")

            pem_file = self.env['cfdi.csd'].browse(
                certificate_id[rec.id]).certificate_key_file_pem

            with open(PEM_F, 'wb') as f_pem:
                f_pem.write(base64.decodebytes(pem_file or ''))
                f_pem.close()

            cer_file = self.env['cfdi.csd'].browse(
                certificate_id[rec.id]).certificate_file

            with open(CER_F, 'wb') as f_cer:
                f_cer.write(base64.decodebytes(cer_file or ''))
                f_cer.close()
