# # coding: utf-8
# # Part of Odoo. See LICENSE file for full copyright and licensing details.

# import base64
# import locale
# import logging
# from datetime import datetime
# try:
#     from StringIO import StringIO  # Python 2
# except ImportError:
#     from io import StringIO  # Python 3

# from lxml import objectify
# from qrcode import ERROR_CORRECT_L, QRCode

from odoo import api, models

# from ..models.account_invoice import AccountInvoice


# _logger = logging.getLogger(__name__)
# try:
#     from num2words import num2words
# except ImportError as err:
#     _logger.debug(err)


# class OmlInvoiceReport(models.AbstractModel):
#     _name = "report.account.report_invoice"

#     @api.multi
#     def render_html(self, data=None):
#         docids = self.ids
#         try:
#             locale.setlocale(locale.LC_TIME, "es_MX.utf8")
#         except BaseException as e:
#             _logger.info('Exception: %s', str(e))
#         invoice_obj = self.env['account.invoice']
#         bom_obj = self.env['mrp.bom']
#         boms = {}
#         for inv in invoice_obj.browse(docids):
#             for line in inv.invoice_line_ids:
#                 if line.product_id.id not in boms.keys():
#                     bom = bom_obj.search([
#                         ('product_id', '=', line.product_id.id)])
#                     if bom and bom.type == 'phantom':
#                         boms[line.product_id.id] = bom
#         uso_cfdi_dict = {
#             'G01': 'Adquisición de mercancias',
#             'G02': 'Devoluciones, descuentos o bonificaciones',
#             'G03': 'Gastos en general',
#             'I01': 'Construcciones',
#             'I02': 'Mobilario y equipo de oficina por inversiones',
#             'I03': 'Equipo de transporte',
#             'I04': 'Equipo de computo y accesorios',
#             'I05': 'Dados, troqueles, moldes, matrices y herramental',
#             'I06': 'Comunicaciones telefónicas',
#             'I07': 'Comunicaciones satelitales',
#             'I08': 'Otra maquinaria y equipo',
#             'D01': 'Honorarios médicos, dentales y gastos hospitalarios.',
#             'D02': 'Gastos médicos por incapacidad o discapacidad',
#             'D03': 'Gastos funerales.',
#             'D04': 'Donativos.',
#             'D05': 'Intereses reales efectivamente pagados por créditos hipotecarios (casa habitación).',
#             'D06': 'Aportaciones voluntarias al SAR.',
#             'D07': 'Primas por seguros de gastos médicos.',
#             'D08': 'Gastos de transportación escolar obligatoria.',
#             'D09': 'Depósitos en cuentas para el ahorro, primas que tengan como base planes de pensiones.',
#             'D10': 'Pagos por servicios educativos (colegiaturas)',
#             'P01': 'Por definir'
#         }
#         docargs = {
#             'doc_ids': docids,
#             'doc_model': 'account.invoice',
#             'docs': invoice_obj.browse(docids),
#             'data': data,
#             'datetime': datetime,
#             'get_xml_data': self._get_xml_data,
#             'split_string': self._split_string,
#             'create_qrcode': self._create_qrcode,
#             'amount_to_text': self._amount_to_text,
#             'invoice_obj': invoice_obj,
#             'get_fiscal_address': self._get_fiscal_address,
#             'get_domicilio': self._get_domicilio,
#             'get_fiscal_regime': self._get_fiscal_regime,
#             'get_comercio_exterior': self._get_comercio_exterior,
#             'bom': boms,
#             'uso_cfdi_dict': uso_cfdi_dict,
#         }
#         return self.env["report"].render("account.report_invoice", docargs)

#     @api.multi
#     def _get_xml_data(self, inv):
#         return objectify.fromstring(inv.xml_signed.encode('utf-8'))

#     def _split_string(self, string, length=135):
#         for i in range(0, len(string or ''), length):
#             string = string[:i] + ' ' + string[i:]
#         return string

#     def _amount_to_text(self, amount, currency, partner_lang='es_MX'):
#         total = str(float(amount)).split('.')[0]
#         decimals = str(float(amount)).split('.')[1]
#         currency_type = 'M.N.'
#         if partner_lang != 'es_MX':
#             total = num2words(float(amount)).upper()
#         else:
#             total = num2words(float(total), lang='es').upper()
#         if currency != 'MXN':
#             currency_type = 'M.E.'
#         else:
#             currency = 'PESOS'
#         return '%s %s %s/100 %s' % (
#             total, currency, decimals or 0.0, currency_type)

#     def _create_qrcode(self, xml):
#         amount_total = float(xml.get('total', xml.get('Total', '')).encode(
#             'ascii', 'replace'))
#         rfc_emisor = xml.Emisor.get('rfc', xml.Emisor.get('Rfc', ''))
#         rfc_receptor = xml.Receptor.get('rfc', xml.Receptor.get('Rfc', ''))
#         uuid = AccountInvoice.l10n_mx_edi_get_tfd_etree(xml).get('UUID', '')
#         amount_total = str.zfill("%0.6f" % amount_total, 17)
#         qrstr = "?re=" + rfc_emisor + "&rr=" + rfc_receptor + "&tt=" +\
#             amount_total + "&id=" + uuid
#         qr = QRCode(version=1, error_correction=ERROR_CORRECT_L)
#         qr.add_data(qrstr)
#         qr.make()  # Generate the QRCode itself
#         im = qr.make_image()
#         f_im = StringIO()
#         im.save(f_im)
#         f_im.seek(0)
#         return base64.encodestring(f_im.read())

#     def _get_fiscal_address(self, emitter, company):
#         return getattr(
#             emitter, 'DomicilioFiscal', company.get_emitter_cfdi())

#     def _get_domicilio(self, receiver, obj):
#         return obj.get_receiver_cfdi_v32()

#     def _get_fiscal_regime(self, emitter, obj):
#         return getattr(
#             emitter, 'RegimenFiscal',
#             {'Regimen': emitter.get('RegimenFiscal')})

#     def _get_comercio_exterior(self, xml):
#         """Get the ComercioExterior node from the cfdi.

#         :param objectify cfdi: The cfdi as etree
#         :return: the ComercioExterior node
#         :rtype: objectify
#         """
#         if not hasattr(xml, 'Complemento'):
#             return {}
#         attribute = 'cce11:ComercioExterior[1]'
#         namespace = {'cce11': 'http://www.sat.gob.mx/ComercioExterior11'}
#         node = xml.Complemento.xpath(attribute, namespaces=namespace)
#         return node[0] if node else {}


class ReportInvoiceWithPayment(models.AbstractModel):
    _inherit = 'report.account.report_invoice_with_payments'
    _description = 'Account report with payment lines'

    @api.model
    def _get_report_values(self, docids, data=None):
        res = super(ReportInvoiceWithPayment, self)._get_report_values(
            docids=docids, data=data)
        boms = {}
        for inv in self.env['account.invoice'].browse(docids):
            for line in inv.invoice_line_ids:
                if line.product_id.id not in boms.keys():
                    bom = self.env['mrp.bom'].search([
                        ('product_id', '=', line.product_id.id)])
                    if bom and bom.type == 'phantom':
                        boms[line.product_id.id] = bom
        res['bom'] = boms
        return res
