# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import locale
import logging
from datetime import datetime

from lxml import objectify

from odoo import api, models

_logger = logging.getLogger(__name__)


class OmlPayrollReport(models.AbstractModel):
    _name = "report.hr_payroll.report_payslip"

    @api.multi
    def _get_report_values(self, docids, data=None):
        try:
            locale.setlocale(locale.LC_TIME, "es_MX.utf8")
        except BaseException as e:
            _logger.info('Exception: %s', str(e))
        inv_report = self.env['report.account.report_invoice']
        invoice_obj = self.env['account.invoice']
        docargs = {
            'doc_ids': docids,
            'doc_model': 'hr.payslip',
            'docs': self.env['hr.payslip'].browse(docids),
            'data': data,
            'datetime': datetime,
            'get_xml_data': self._get_xml_data,
            'get_payroll_data': self._get_payroll_data,
            'get_overtime_data': self._get_overtime_data,
            'get_other_payment_data': self._get_other_payment_data,
            'split_string': inv_report._split_string,
            'create_qrcode': inv_report._create_qrcode,
            'amount_to_text': inv_report._amount_to_text,
            'invoice_obj': invoice_obj,
        }
        return self.env["report"].render("hr_payroll.report_payslip", docargs)

    @api.multi
    def _get_xml_data(self, pay):
        xml = base64.decodestring(pay.l10n_mx_edi_cfdi)
        return objectify.fromstring(xml)

    @api.model
    def _get_payroll_data(self, xml):
        """Return payroll section from XML"""
        return xml.Complemento.xpath(
            'nomina12:Nomina',
            namespaces={'nomina12': 'http://www.sat.gob.mx/nomina12'})[0]

    @api.model
    def _get_overtime_data(self, xml):
        """Return overtime section from XML if are found"""
        overtime = []
        for line in xml.Percepciones.Percepcion:
            overtime.extend(line.xpath('nomina12:HorasExtra', namespaces={
                'nomina12': 'http://www.sat.gob.mx/nomina12'}))
        return overtime

    @api.model
    def _get_other_payment_data(self, xml):
        """Return other payments section from XML if are found"""
        return xml.xpath('nomina12:OtrosPagos', namespaces={
            'nomina12': 'http://www.sat.gob.mx/nomina12'})
