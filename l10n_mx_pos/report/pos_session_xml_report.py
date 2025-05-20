# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
import locale
import logging
from datetime import datetime

from lxml import objectify

from odoo import api, models

_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError as err:
    _logger.debug(err)


class SessionXmlReport(models.AbstractModel):
    _name = "report.l10n_mx_pos.report_xml_session"

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'pos.session'
        #report_obj = self.env["report"]
        #report = report_obj._get_report_from_name(
        #    "l10n_mx_pos.report_xml_session")
        try:
            locale.setlocale(locale.LC_TIME, "es_MX.utf8")
        except BaseException as e:
            _logger.info(str(e))
        invoice_report = self.env['report.account.report_invoice']
        docargs = {
            "doc_ids": docids,
            #"doc_model": report.model,
            'doc_model': self.model,
            'docs': self.env['pos.session'].browse(docids),
            'get_xml_data': self._get_xml_data,
            'datetime': datetime,
            'split_string': invoice_report._split_string,
            'create_qrcode': invoice_report._create_qrcode,
            'amount_to_text': self._amount_to_text,
            'context': dict(self.env.context or {}),
            'invoice_obj': self.env['account.invoice'],
            'get_fiscal_address': invoice_report._get_fiscal_address,
            'get_domicilio': self._get_domicilio,
            'get_fiscal_regime': invoice_report._get_fiscal_regime,
        }

        #return report_obj.render("l10n_mx_pos.report_xml_session", docargs)
        return docargs

    @api.multi
    def _get_xml_data(self, session):
        name = "%s_%s.xml" % (session.name, 'to_print')
        attachment = self.env['ir.attachment'].search([
            ('res_id', '=', session.id),
            ('res_model', '=', session._name),
            ('name', '=', name)], limit=1)
        return objectify.fromstring(base64.decodestring(attachment.datas))

    def _amount_to_text(self, amount):
        total = str(float(amount)).split('.')[0]
        decimals = str(float(amount)).split('.')[1]
        currency_type = 'M.N.'
        currency = 'PESOS'
        total = num2words(float(total), lang='es').upper()
        return '%s %s %s/100 %s' % (
            total, currency, decimals or 0.0, currency_type)

    def _get_domicilio(self, receiver, obj):
        return getattr(
            receiver, 'Domicilio', {'pais': self.env.ref('base.mx').name})
