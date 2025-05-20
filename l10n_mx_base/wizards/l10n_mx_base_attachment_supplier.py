# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OmlAttachmentWizard(models.TransientModel):

    _name = "l10n_mx_base.attachment.wizard"

    name = fields.Char(
        readonly=True, help='Name of attachment generated')
    company_id = fields.Many2one(
        'res.company', 'Company', readonly=True,
        help='Company to which it belongs this attachment')
    xml_name = fields.Char(help='Save the file name, to verify that is .xml')
    pdf_name = fields.Char(help='Save the file name, to verify that is .pdf')
    file_xml_sign = fields.Binary(
        'File XML sign',
        help='This file .xml is proportionate by the supplier', required=True)
    file_pdf = fields.Binary(
        help='This file .pdf is proportionate by the supplier', required=True)

    @api.multi
    def attach(self):
        xml_extension = os.path.splitext(self.xml_name)[1].lower()
        pdf_extension = os.path.splitext(self.pdf_name)[1].lower()
        if any([xml_extension != '.xml', pdf_extension != '.pdf']):
            raise ValidationError(_(
                'Verify that files are .xml and .pdf, please!'))
        inv_obj = self.env['account.invoice']
        invoice_id = self.env.context.get('active_id', False)
        invoice = inv_obj.browse(invoice_id)
        if not invoice._validate_invoice_xml(self.file_xml_sign):
            return False
        att_obj = self.env['ir.attachment']
        fname = '%s.pdf' % invoice.l10n_mx_report_name
        att_obj.create({
            'name': fname,
            'datas': self.file_pdf,
            'datas_fname': fname,
            'res_model': 'account.invoice',
            'res_id': invoice.id})
        return True
