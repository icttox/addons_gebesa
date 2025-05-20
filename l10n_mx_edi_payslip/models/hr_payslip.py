# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division

import time
import logging
import base64
import cgi
import re

from lxml import objectify, etree
from suds.client import Client

from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)

try:
    from cfdilib import cfdv33
except ImportError as err:
    _logger.debug(err)


def create_list_html(array):
    """Convert an array of string to a html list.
    :param list array: A list of strings
    :return: an empty string if not array, an html list otherwise.
    :rtype: str"""
    if not array:  # pragma: no cover
        return ''  # pragma: no cover
    msg = ''
    for item in array:
        msg += '<li>' + item + '</li>'
    return '<ul>' + msg + '</ul>'


class HrPayslipInability(models.Model):
    _name = 'hr.payslip.inability'

    payslip_id = fields.Many2one(
        'hr.payslip', required=True, ondelete='cascade',
        help='Payslip related with this inability')
    sequence = fields.Integer(required=True, default=10)
    days = fields.Integer(
        help='Number of days in which the employee performed inability in '
        'the payslip period', required=True)
    inability_type = fields.Selection(
        [('01', 'Risk of work'),
         ('02', 'Disease in general'),
         ('03', 'Maternity')], 'Type', required=True, default='01',
        help='Reason for inability: Catalog published in the SAT portal')
    amount = fields.Float(help='Amount for the inability', required=True)


class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'mail.thread']

    l10n_mx_edi_payment_date = fields.Date(
        'Payment Date', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        default=time.strftime('%Y-%m-01'), help='Save the payment date that '
        'will be added on CFDI.')
    l10n_mx_edi_cfdi_name = fields.Char(
        string='CFDI name', copy=False, readonly=True,
        help='The attachment name of the CFDI.')
    l10n_mx_edi_cfdi = fields.Binary(
        'CFDI content', copy=False, readonly=True,
        help='The cfdi xml content encoded in base64.',
        compute='_compute_cfdi_values')
    l10n_mx_edi_inability_line_ids = fields.One2many(
        'hr.payslip.inability', 'payslip_id', 'Inabilities',
        readonly=True, states={'draft': [('readonly', False)]},
        help='Used in XML like optional node to express disabilities '
        'applicable by employee.', copy=True)
    l10n_mx_edi_overtime_line_ids = fields.One2many(
        'hr.payslip.overtime', 'payslip_id', 'Extra hours',
        readonly=True, states={'draft': [('readonly', False)]},
        help='Used in XML like optional node to express the extra hours '
        'applicable by employee.', copy=True)
    l10n_mx_edi_pac_status = fields.Selection(
        [('retry', 'Retry'),
         ('to_sign', 'To sign'),
         ('signed', 'Signed'),
         ('to_cancel', 'To cancel'),
         ('cancelled', 'Cancelled')], 'PAC status',
        help='Refers to the status of the invoice inside the PAC.',
        readonly=True, copy=False)
    l10n_mx_edi_sat_status = fields.Selection(
        [('none', 'State not defined'),
         ('undefined', 'Not Synced Yet'),
         ('not_found', 'Not Found'),
         ('cancelled', 'Cancelled'),
         ('valid', 'Valid')], 'SAT status',
        help='Refers to the status of the invoice inside the SAT system.',
        readonly=True, copy=False, required=True, track_visibility='onchange',
        default='undefined')
    l10n_mx_edi_cfdi_uuid = fields.Char(
        'Fiscal Folio', copy=False, readonly=True,
        help='Folio in electronic payroll, is returned by SAT when send to '
        'stamp.', compute='_compute_cfdi_values')
    l10n_mx_edi_cfdi_supplier_rfc = fields.Char(
        'Supplier RFC', copy=False, readonly=True,
        help='The supplier tax identification number.',
        compute='_compute_cfdi_values')
    l10n_mx_edi_cfdi_customer_rfc = fields.Char(
        'Customer RFC', copy=False, readonly=True,
        help='The customer tax identification number.',
        compute='_compute_cfdi_values')
    l10n_mx_edi_cfdi_amount = fields.Float(
        'Total Amount', copy=False, readonly=True,
        help='The total amount reported on the cfdi.',
        compute='_compute_cfdi_values')
    l10n_mx_edi_action_title_ids = fields.One2many(
        'hr.payslip.action.titles', 'payslip_id', string='Action or Titles',
        help='If the payslip have perceptions with code 045, assign here the '
        'values to the attribute in XML, use the perception type to indicate '
        'if apply to exempt or taxed.')
    l10n_mx_edi_extra_node_ids = fields.One2many(
        'hr.payslip.extra.perception', 'payslip_id',
        string='Extra data to perceptions',
        help='If the payslip have perceptions with code in 022, 023 or 025,'
        'must be created a record with data that will be assigned in the '
        'node "SeparacionIndemnizacion", or if the payslip have perceptions '
        'with code in 039 or 044 must be created a record with data that will '
        'be assigned in the node "JubilacionPensionRetiro". Only must be '
        'created a record by node.')
    l10n_mx_edi_subsidy = fields.Float(
        'Subsidy Caused', help='If the payslip include other payments, and '
        'one of this records have the code 002 is need add the subsidy '
        'caused to assign in node "SubsidioAlEmpleo".')
    l10n_mx_edi_balance_favor = fields.Float(
        'Balance in Favor', help='If the payslip include other payments, and '
        'one of this records have the code 004 is need add the balance in '
        'favor to assign in node "CompensacionSaldosAFavor".')
    l10n_mx_edi_comp_year = fields.Integer(
        'Year', help='If the payslip include other payments, and '
        'one of this records have the code 004 is need add the year to assign '
        'in node "CompensacionSaldosAFavor".')
    l10n_mx_edi_remaining = fields.Float(
        'Remaining', help='If the payslip include other payments, and '
        'one of this records have the code 004 is need add the remaining to '
        'assign in node "CompensacionSaldosAFavor".')
    l10n_mx_edi_source_resource = fields.Selection([
        ('IP', 'Own income'),
        ('IF', 'Federal income'),
        ('IM', 'Mixed income')], 'Source Resource',
        help='Used in XML to identify the source of the resource used '
        'for the payment of payroll of the personnel that provides or '
        'performs a subordinate or assimilated personal service to salaries '
        'in the dependencies. This value will be set in the XML attribute '
        '"OrigenRecurso" to node "EntidadSNCF".')
    l10n_mx_edi_amount_sncf = fields.Float(
        'Own resource', help='When the attribute in "Source Resource" is "IM" '
        'this attribute must be added to set in the XML attribute '
        '"MontoRecursoPropio" in node "EntidadSNCF", and must be less that '
        '"TotalPercepciones" + "TotalOtrosPagos"')
    l10n_mx_edi_cfdi_string = fields.Char(
        'CFDI Original String', help='Attribute "cfdi_cadena_original" '
        'returned by PAC request when is stamped the CFDI, this attribute is '
        'used on report.')
    # Add parameter copy=True
    input_line_ids = fields.One2many(copy=True)
    l10n_mx_edi_usage = fields.Selection(
        '_get_l10n_mx_edi_usages', default='P01', string='Usage',
        help='Used in CFDI v3.3 to express the key of the use the receiver '
        'will give to this invoice. This value is defined by the '
        'customer. \nNote: It is not a cause for cancellation if the key set '
        'is not the use the receiver will give the document.')

    def _get_l10n_mx_edi_usages(self):
        return [
            ('D01', 'Medical, dental and hospital expenses.'),
            ('D02', 'Medical expenses for disability'),
            ('D03', 'Funeral expenses'),
            ('D04', 'Donations'),
            ('D05',
             'Real interest effectively paid for mortgage loans (room house)'),
            ('D06', 'Voluntary contributions to SAR'),
            ('D07', 'Medical insurance premiums'),
            ('D08', 'Mandatory School Transportation Expenses'),
            ('D09',
             'Deposits in savings accounts, premiums based on pension plans.'),
            ('D10', 'Payments for educational services (Colegiatura)'),
            ('G01', 'Acquisition of merchandise'),
            ('G02', 'Returns, discounts or bonuses'),
            ('G03', 'General expenses'),
            ('I01', 'Constructions'),
            ('I02', 'Office furniture and equipment investment'),
            ('I03', 'Transportation equipment'),
            ('I04', 'Computer equipment and accessories'),
            ('I05', 'Dices, dies, molds, matrices and tooling'),
            ('I06', 'Telephone communications'),
            ('I07', 'Satellite communications'),
            ('I08', 'Other machinery and equipment'),
            ('P01', 'To define')]

    @api.multi
    def action_payslip_done(self):
        """Generates the cfdi attachments for mexican companies when validated.
        """
        result = super(HrPayslip, self).action_payslip_done()
        for record in self:
            if record.company_id.country_id == self.env.ref('base.mx'):
                record.l10n_mx_edi_cfdi_name = ('%s-MX-Payroll-3-2.xml' % (
                    self.number)).replace('/', '')
                record._l10n_mx_edi_retry()
        return result

    @api.multi
    def _l10n_mx_edi_retry(self):
        """Try to generate the cfdi attachment and then, sign it."""
        for record in self:
            cfdi_values = record._l10n_mx_edi_create_cfdi()
            error = cfdi_values.pop('error', None)
            cfdi = cfdi_values.pop('cfdi', None)
            if error:
                # cfdi failed to be generated
                record.l10n_mx_edi_pac_status = 'retry'
                record.message_post(body=error)
                continue
            # cfdi has been successfully generated
            record.l10n_mx_edi_pac_status = 'to_sign'

            ctx = self.env.context.copy()
            ctx.pop('default_type', False)
            filename = (
                '%s-MX-Payroll-3-2.xml' % (record.number)).replace('/', '')
            record.l10n_mx_edi_cfdi_name = filename
            attach_id = self.env['ir.attachment'].with_context(ctx).create({
                'name': filename,
                'res_id': record.id,
                'res_model': record._name,
                'datas': base64.encodestring(cfdi),
                'datas_fname': filename,
                'description': 'Mexican payroll',
            })
            record.message_post(
                body=_('CFDI document generated (may be not signed)'),
                attachment_ids=[attach_id.id])
            record._l10n_mx_edi_sign()

    @api.multi
    @api.depends('l10n_mx_edi_cfdi_name')
    def _compute_cfdi_values(self):
        """Fill the payroll fields from the CFDI values."""
        invoice_obj = self.env['account.invoice']
        for record in self:
            attachment_id = record.l10n_mx_edi_retrieve_last_attachment()
            if not attachment_id:
                continue
            # At this moment, the attachment contains the file size in its
            # 'datas' field because to save some memory, the attachment will
            # store its data on the physical disk.
            # To avoid this problem, we read the 'datas' directly on the disk.
            datas = attachment_id._file_read(attachment_id.store_fname)
            record.l10n_mx_edi_cfdi = datas
            tree = record.l10n_mx_edi_get_xml_etree(base64.decodestring(datas))
            # if already signed, extract uuid
            tfd_node = invoice_obj.l10n_mx_edi_get_tfd_etree(tree)
            if tfd_node is not None:
                record.l10n_mx_edi_cfdi_uuid = tfd_node.get('UUID')
            record.l10n_mx_edi_cfdi_amount = tree.get('total')
            record.l10n_mx_edi_cfdi_supplier_rfc = tree.Emisor.get('rfc')
            record.l10n_mx_edi_cfdi_customer_rfc = tree.Receptor.get('rfc')

    @api.model
    def l10n_mx_edi_retrieve_attachments(self):
        """Retrieve all the CFDI attachments generated for this payroll.
        Returns:
            recordset: An ir.attachment recordset"""
        self.ensure_one()
        if not self.l10n_mx_edi_cfdi_name:
            return []
        domain = [
            ('res_id', '=', self.id),
            ('res_model', '=', self._name),
            ('name', '=', self.l10n_mx_edi_cfdi_name)]
        return self.env['ir.attachment'].search(domain)

    @api.model
    def l10n_mx_edi_retrieve_last_attachment(self):
        attachment_ids = self.l10n_mx_edi_retrieve_attachments()
        return attachment_ids[0] if attachment_ids else None

    @api.model
    def l10n_mx_edi_get_xml_etree(self, cfdi=None):
        """Get an objectified tree representing the cfdi.
        If the cfdi is not specified, retrieve it from the attachment.
        :param str cfdi: The cfdi as string
        :return: An objectified tree
        :rtype: objectify"""
        # TODO helper which is not of too much help and should be removed
        self.ensure_one()
        if cfdi is None:
            cfdi = base64.decodestring(self.l10n_mx_edi_cfdi)
        return objectify.fromstring(cfdi)

    @api.multi
    def _l10n_mx_edi_call_service(self, service_type):
        """Call the right method according to the service_type, it's info
        returned
        :param str service_type: sign or cancel
        """
        invoice_obj = self.env['account.invoice']
        for record in self:
            # This sequence is used to payroll records
            pac = self.env.ref('hr_payroll.seq_salary_slip').pac_id
            cfdi = base64.decodestring(record.l10n_mx_edi_cfdi)
            if not pac:
                continue
            if service_type == 'sign':
                response = invoice_obj._vauxoo_stamp(cfdi, pac)
                xml_signed = response.get('cfdi_xml', '')
                if xml_signed:
                    xml_signed = base64.encodestring(
                        xml_signed.encode('utf-8'))
                    record.l10n_mx_edi_cfdi_string = response.get(
                        'cfdi_cadena_original', '')
                msg = response.get('error', '')
                record._l10n_mx_edi_post_sign_process(xml_signed, msg=msg)
            elif service_type == 'cancel':
                certificate = record.company_id.certificate_id
                cer = certificate.file_pem
                key = base64.decodestring(certificate.file_key_pem)
                password = certificate.password
                response = invoice_obj._vauxoo_cancel(
                    pac, cfdi, cer, key, password)
                cancelled = response.get('cancellation_date', False)
                msg = response.get('message')
                record._l10n_mx_edi_post_cancel_process(cancelled, msg)

    @api.multi
    def _l10n_mx_edi_post_cancel_process(self, cancelled, code=None, msg=None):
        """Post process the results of the cancel service.
        :param bool cancelled: is the cancel has been done with success
        :param str code: an eventual error code
        :param str msg: an eventual error msg"""

        self.ensure_one()
        if cancelled:
            body_msg = _('The cancel service has been called with success')
            self.l10n_mx_edi_pac_status = 'cancelled'
        else:
            body_msg = _('The cancel service requested failed')
        post_msg = []
        if code:
            post_msg.extend([_('Code: ') + str(code)])
        if msg:
            post_msg.extend([_('Message: ') + msg])
        self.message_post(
            body=body_msg + create_list_html(post_msg),
            subtype='account.mt_invoice_validated')

    @api.multi
    def _l10n_mx_edi_post_sign_process(self, xml_signed, code=None, msg=None):
        """Post process the results of the sign service.
        :param bool xml_signed: the xml signed datas codified in base64
        :param str code: an eventual error code
        :param str msg: an eventual error msg
        """
        self.ensure_one()
        if xml_signed:
            body_msg = _('The sign service has been called with success')
            # Update the pac status
            self.l10n_mx_edi_pac_status = 'signed'
            self.l10n_mx_edi_cfdi = xml_signed
            # Update the content of the attachment
            attachment_id = self.l10n_mx_edi_retrieve_last_attachment()
            attachment_id.write({
                'datas': xml_signed,
                'mimetype': 'application/xml'
            })
            post_msg = [_('The content of the attachment has been updated')]
        else:
            body_msg = _('The sign service requested failed')
            post_msg = []
        if code:
            post_msg.extend([_('Code: ') + str(code)])
        if msg:
            post_msg.extend([_('Message: ') + msg])
        self.message_post(
            body=body_msg + create_list_html(post_msg))

    @api.multi
    def _l10n_mx_edi_sign(self):
        """Call the sign service with records that can be signed."""
        records = self.filtered(lambda r: r.l10n_mx_edi_pac_status not in [
            'signed', 'to_cancel', 'cancelled', 'retry'])
        records._l10n_mx_edi_call_service('sign')

    @api.multi
    def _l10n_mx_edi_create_cfdi_values(self):
        """Create the values to fill the CFDI template."""
        self.ensure_one()
        invoice_obj = self.env['account.invoice']
        payroll = self.get_payroll_12()
        if payroll.get('error', False):
            return payroll
        subtotal = payroll['total_other'] + payroll['total_perceptions']
        deduction = payroll['total_deductions']
        total = subtotal - deduction
        payslip = {
            'date_invoice_tz': invoice_obj.datetime_cfdi(),
            'payment_policy': '99',
            'number': self.id,
            'payment_conditions': 'NA',
            'document_type': 'N',
            'amount_total': "%.2f" % abs(total or 0.0),
            'subtotal': "%.2f" % abs(subtotal or 0.0),
            'subtotal_wo_discount': "%.2f" % abs(subtotal or 0.0),
            'discount_amount': "%.2f" % abs(deduction or 0.0),
            'serie': self.get_string_cfdi(self.number),
            'taxes': {
                'total_transferred': '0.00',
                'total_withhold': '0.00',
            },
            'payroll': payroll,
            'currency': 'MXN',
            'rate': 1,
            'not_show_address': True,
            'receiver_use_cfdi': self.l10n_mx_edi_usage,
        }
        payslip['invoice_lines'] = [{
            'name': u'Pago de nómina',
            'price_unit': "%.2f" % abs(subtotal or 0.0),
            'subtotal_wo_discount': "%.2f" % abs(subtotal or 0.0),
            'discount': "%.2f" % abs(deduction or 0.0),
        }]
        payslip.update(self.company_id.get_emitter_cfdi())
        payslip.update(
            self.employee_id.address_home_id._get_receiver_address())
        return payslip

    @api.multi
    def get_payroll_12(self):
        self.ensure_one()
        company = self.company_id
        employee = self.employee_id
        contracts = employee.contract_ids.sorted(key=lambda r: r.date_start)
        if not contracts:
            return {'error': _('Employee has not a contract and is required')}
        date_start = fields.Date.from_string(contracts[0].date_start)
        date = fields.Date.from_string(self.l10n_mx_edi_payment_date)
        seniority = ((date - date_start).days - 1) / 7
        payroll = {
            'type': 'O',  # TODO, Cuando E y cuando O
            'payment_date': self.l10n_mx_edi_payment_date,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'number_of_days': int(sum(self.worked_days_line_ids.mapped(
                'number_of_days'))),
            'curp_emitter': company.l10n_mx_edi_curp or '',
            'employer_register': company.company_registry or '',
            'vat_emitter': self.company_id.vat,
            'source_sncf': self.l10n_mx_edi_source_resource or '',
            'amount_sncf': self.l10n_mx_edi_amount_sncf or '',
            'inabilities': self.get_inabilities(),
            'date_start': contracts[0].date_start,
            'seniority_emp': 'P%sW' % int(seniority),
        }
        payroll.update(employee.get_cfdi_employee_data(self.contract_id))
        payroll.update(self.get_cfdi_perceptions_data())
        payroll.update(self.get_cfdi_deductions_data())
        payroll.update(self.get_cfdi_other_payments_data())
        payroll.update(self.get_cfdi_extra_perceptions())
        return payroll

    @api.multi
    def get_inabilities(self):
        self.ensure_one()
        return [{'days': i.days, 'type': i.inability_type, 'amount': i.amount}
                for i in self.l10n_mx_edi_inability_line_ids]

    @api.multi
    def get_cfdi_extra_perceptions(self):
        """If some perception have code in 022, 023, 025 add values to node
        SeparacionIndemnizacion, or if some perception have code in 039 or
        044 add values to node JubilacionPensionRetiro."""
        categ_g = self.env.ref(
            'l10n_mx_edi_payslip.hr_salary_rule_category_perception_mx_taxed')
        categ_e = self.env.ref(
            'l10n_mx_edi_payslip.hr_salary_rule_category_perception_mx_exempt')
        lines = self.line_ids.filtered('total').filtered(
            lambda r: r.category_id in [categ_g, categ_e])
        extra_nodes = {}
        if lines.filtered(lambda r: r.code[2:] in ['022', '023', '025']):
            sep = self.l10n_mx_edi_extra_node_ids.filtered(
                lambda r: r.node == 'separation')
            extra_nodes.update({
                'compensation_paid': sep.amount_total,
                'compensation_years': sep.service_years,
                'compensation_last_salary': sep.last_salary,
                'compensation_cumulative': sep.accumulable_income,
                'compensation_no_cumulative': sep.non_accumulable_income,
            })
        retirement = lines.filtered(lambda r: r.code[2:] in ['039', '044'])
        if retirement:
            ret = self.l10n_mx_edi_extra_node_ids.filtered(
                lambda r: r.node == 'retirement')
            extra_nodes.update({
                'retirement_one_ex': ret.amount_total if retirement.code[2:] == '039' else 0.0,  # noqa
                'retirement_partiality': ret.amount_total if retirement.code[2:] == '044' else 0.0,  # noqa
                'retirement_amount_diary': ret.amount_daily,
                'retirement_cumulative': ret.accumulable_income,
                'retirement_no_cumulative': ret.non_accumulable_income,
            })
        return extra_nodes

    @api.multi
    def get_cfdi_perceptions_data(self):
        perceptions = []
        categ_g = self.env.ref(
            'l10n_mx_edi_payslip.hr_salary_rule_category_perception_mx_taxed')
        categ_e = self.env.ref(
            'l10n_mx_edi_payslip.hr_salary_rule_category_perception_mx_exempt')
        lines = self.line_ids.filtered('total')
        taxed, total_taxed = lines._get_perceptions_taxed()
        exempt, total_exempt = lines._get_perceptions_exempt()
        extra_lines = lines._get_extra_lines()
        perceptions.extend(taxed)
        perceptions.extend(exempt)
        perceptions.extend(extra_lines)
        salaries = sum(self.line_ids.filtered(
            lambda r: r.category_id in [categ_e, categ_g] and
            r.code[2:] not in ['022', '023', '025', '039', '044']).mapped(
                'total'))
        compensation = sum(self.line_ids.filtered(
            lambda r: r.category_id in [categ_e, categ_g] and
            r.code[2:] in ['022', '023', '025']).mapped('total'))
        retirement = sum(self.line_ids.filtered(
            lambda r: r.category_id in [categ_e, categ_g] and
            r.code[2:] in ['039', '044']).mapped('total'))
        return {
            'total_salaries': salaries,
            'total_compensation': compensation,
            'total_retirement': retirement,
            'total_taxed': total_taxed,
            'total_exempt': total_exempt,
            'total_perceptions': salaries + compensation + retirement,
            'perceptions': perceptions,
        }

    @api.multi
    def get_cfdi_deductions_data(self):
        categ = self.env.ref(
            'l10n_mx_edi_payslip.hr_salary_rule_category_deduction_mx')
        deductions = []
        total = 0.0
        total_other = 0.0
        total_withheld = 0.0
        show_total_taxes_withheld = False
        for deduction in self.line_ids.filtered(
                lambda r: r.category_id == categ and r.amount):
            deductions.append({
                'type': deduction.code,
                'key': deduction.code,
                'concept': deduction.name[:100],
                'amount': abs(deduction.total),
            })
            total += deduction.total
            if deduction.code != '002':
                total_other += deduction.total
            else:
                show_total_taxes_withheld = True
                total_withheld = deduction.total
        return {
            'total_deductions': abs(total),
            'total_other_deductions': abs(total_other),
            'show_total_taxes_withheld': show_total_taxes_withheld,
            'total_taxes_withheld': abs(total_withheld),
            'deductions': deductions,
        }

    @api.multi
    def get_cfdi_other_payments_data(self):
        """Records with category Other Payments are used in the node
        "OtrosPagos".
        If a record have code 002, the node "SubsidioAlEmpleo" must be added
        If a necord have code 004, the node "CompensacionSaldosAFavor" must be
        added."""
        categ = self.env.ref(
            'l10n_mx_edi_payslip.hr_salary_rule_category_other_mx')
        other_payments = []
        total_other = 0.0
        for other in self.line_ids.filtered(
                lambda r: r.category_id == categ and r.amount):
            payment = {
                'type': other.code[2:],
                'key': other.code,
                'concept': other.name[:100],
                'amount': abs(other.total),
            }
            if other.code[2:] == '002':
                payment.update({
                    'subsidy': self.l10n_mx_edi_subsidy,
                })
            elif other.code[2:] == '004':
                payment.update({
                    'compensation': {
                        'amount': self.l10n_mx_edi_balance_favor,
                        'year': self.l10n_mx_edi_comp_year,
                        'rem': self.l10n_mx_edi_remaining,
                    }
                })
            other_payments.append(payment)
            total_other += abs(other.total)
        return {
            'total_other': total_other,
            'other_payments': other_payments,
        }

    @api.multi
    def _l10n_mx_edi_create_cfdi(self):
        """Creates and returns a dictionnary containing 'cfdi' if the cfdi is
        well created, 'error' otherwise."""
        self.ensure_one()
        error_log = []
        values = self._l10n_mx_edi_create_cfdi_values()

        # -----------------------
        # Check the configuration
        # -----------------------
        # - Check not errors in values generation
        if values.get('error'):
            error_log.append(values.get('error'))

        # -Check certificate
        certificate_id = self.company_id.certificate_id
        if not certificate_id:
            error_log.append(_('No valid certificate found'))

        # -Check PAC
        pac = self.env.ref('hr_payroll.seq_salary_slip').pac_id
        if not pac:
            error_log.append(_('No PAC specified.'))

        if error_log:
            return {'error': _(
                'Please check your configuration: ') + create_list_html(
                    error_log)}

        # -----------------------
        # Create the EDI document
        # -----------------------

        # -Compute certificate data
        values['certificate_number'] = certificate_id.serial_number
        values['certificate'] = certificate_id.content_pem

        # -Compute cfdi
        # Then get an cfdilib invoice object in order to prepare all the
        # template stuff.
        payslip = cfdv33.get_payroll(values)
        if bool(payslip.ups):
            return {'error': _(
                'The CFDI generated is not valid') + create_list_html(
                    payslip.ups)}
        cfdi = objectify.fromstring(payslip.document)

        return {'cfdi': etree.tostring(
            cfdi, pretty_print=True, xml_declaration=True, encoding='UTF-8')}

    @api.multi
    def l10n_mx_edi_update_pac_status(self):
        """Synchronize both systems: Odoo & PAC if the payrolls need to be
        signed or cancelled."""
        for record in self:
            if record.l10n_mx_edi_pac_status == 'to_sign':
                record._l10n_mx_edi_sign()
            elif record.l10n_mx_edi_pac_status == 'to_cancel':
                record._l10n_mx_edi_cancel()
            elif record.l10n_mx_edi_pac_status == 'retry':
                record._l10n_mx_edi_retry()

    @api.multi
    def l10n_mx_edi_update_sat_status(self):
        """Synchronize both systems: Odoo & SAT to make sure the payroll is
        valid."""
        url = 'https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc?wsdl'  # noqa
        cfdi_sat_status = {
            'No Encontrado': 'not_found',
            'Cancelado': 'cancelled',
            'Vigente': 'valid',
        }
        for record in self:
            if record.l10n_mx_edi_pac_status not in ['signed', 'cancelled']:
                continue
            supplier_rfc = record.l10n_mx_edi_cfdi_supplier_rfc
            customer_rfc = record.l10n_mx_edi_cfdi_customer_rfc
            total = record.l10n_mx_edi_cfdi_amount
            uuid = record.l10n_mx_edi_cfdi_uuid
            try:
                response = Client(url).service.Consulta(
                    '"?re=%s&rr=%s&tt=%s&id=%s' % (
                        cgi.escape(cgi.escape(supplier_rfc or '')),
                        cgi.escape(cgi.escape(customer_rfc or '')),
                        total or 0.0, uuid or '')).Estado
            except BaseException as e:  # pragma: no cover
                record.l10n_mx_edi_log_error(str(e) or e.reason.__repr__())  # noqa pragma: no cover
                continue  # pragma: no cover
            record.l10n_mx_edi_sat_status = cfdi_sat_status.get(
                response.__repr__(), 'none')

    @api.multi
    def action_payslip_cancel(self):
        """Overwrite method when state is done, to allow cancel payslip in done
        """
        res = True
        for slip in self:
            if slip.state == 'done':
                slip.write({'state': 'cancel'})
            else:
                res = super(HrPayslip, slip).action_payslip_cancel()
        self._l10n_mx_edi_cancel()
        return res

    @api.multi
    def _l10n_mx_edi_cancel(self):
        """Call the cancel service with records that can be signed."""
        records = self.filtered(lambda r: r.l10n_mx_edi_pac_status in [
            'to_sign', 'signed', 'to_cancel', 'retry'])
        for record in records:
            if record.l10n_mx_edi_pac_status in ['to_sign', 'retry']:
                record.l10n_mx_edi_pac_status = 'cancelled'
                record.message_post(body=_(
                    'The cancel service has been called with success'),
                    subtype='account.mt_invoice_validated')
            else:
                record.l10n_mx_edi_pac_status = 'to_cancel'
        records = self.filtered(
            lambda r: r.l10n_mx_edi_pac_status == 'to_cancel')
        records._l10n_mx_edi_call_service('cancel')

    @api.multi
    def action_payroll_sent(self):
        """ Open a window to compose an email, with the edi payslip template
        message loaded by default"""
        self.ensure_one()
        template = self.env.ref(
            'l10n_mx_edi_payslip.email_template_edi_payroll', False)
        compose_form = self.env.ref(
            'mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='hr.payslip',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @staticmethod
    def get_string_cfdi(text, size=100):
        """Replace from text received the characters that are not found in the
        regex. This regex is taken from SAT documentation."""
        __check_cfdi_re = re.compile(u(r'''([A-Z]|[a-z]|[0-9]| |Ñ|ñ|!|"|%|&|'|´|-|:|;|>|=|<|@|_|,|\{|\}|`|~|á|é|í|ó|ú|Á|É|Í|Ó|Ú|ü|Ü)'''))  # noqa
        for char in __check_cfdi_re.sub('', text):
            text = text.replace(char, ' ')
        return text.strip()[:size]


class HrEmployee(models.Model):

    _inherit = "hr.employee"

    def _default_domain_employee_regime(self):
        """The SAT provide the catalog to employee fiscal regime, like the
        model fiscal.position is used with other data, only allow return the
        data required in the XML node to employee."""
        xml_ids = [
            'account_fiscal_position_02_emp', 'account_fiscal_position_03_emp',
            'account_fiscal_position_04_emp', 'account_fiscal_position_05_emp',
            'account_fiscal_position_06_emp', 'account_fiscal_position_07_emp',
            'account_fiscal_position_08_emp', 'account_fiscal_position_09_emp',
            'account_fiscal_position_10_emp', 'account_fiscal_position_11_emp',
            'account_fiscal_position_99_emp']
        ids = []
        for xml in xml_ids:
            xml = self.env.ref('l10n_mx_edi_payslip.%s' % xml,
                               raise_if_not_found=False)
            ids.append(xml.ids if xml else [])
        return [('id', 'in', ids)]

    l10n_mx_edi_nss = fields.Char(
        'NSS', size=15, help='Optional attribute for the expression of Social '
        'Security Number applicable to the worker')
    l10n_mx_edi_curp = fields.Char('CURP', help="Worker CURP", size=18)
    l10n_mx_edi_syndicated = fields.Boolean(
        'Syndicated', help='Used in the XML to indicate if the worker is '
        'associated with a union. If it is omitted, it is assumed that it is '
        'not associated with any union.')
    l10n_mx_edi_risk_rank = fields.Selection([
        ('1', 'Class I'),
        ('2', 'Class II'),
        ('3', 'Class III'),
        ('4', 'Class IV'),
        ('5', 'Class V')], 'Risk Rank',
        help='Used in the XML to express the key according to the Class in '
        'which the employers must register, according to the activities '
        'carried out by their workers, as provided in article 196 of the '
        'Regulation on Affiliation Classification of Companies, Collection '
        'and Inspection, or in accordance with the regulations Of the Social '
        'Security Institute of the worker.')
    l10n_mx_edi_fiscal_regime_id = fields.Many2one(
        'account.fiscal.position', company_dependent=True,
        string="Fiscal Regime",
        help='Used in XML to express the key of regime for which the worker '
        'has been hired.',
        domain=lambda self: self._default_domain_employee_regime())

    @api.multi
    def get_cfdi_employee_data(self, contract):
        self.ensure_one()
        regime = self.l10n_mx_edi_fiscal_regime_id
        return {
            'curp_emp': self.l10n_mx_edi_curp,
            'nss_emp': self.l10n_mx_edi_nss or '',
            'contract_type': contract.type_id.l10n_mx_edi_code,
            'emp_syndicated': 'Si' if self.l10n_mx_edi_syndicated else 'No',
            'working_day': self.get_working_date(),
            'emp_regimen_type': regime.name[:2] if regime else '',
            'no_emp': self.id,
            'departament': self.department_id.name,
            'emp_job': self.job_id.name,
            'emp_risk': self.l10n_mx_edi_risk_rank or '',
            'payment_periodicity': self.contract_id.schedule_pay,
            'emp_bank': self.bank_account_id.bank_id.code or '',
            'emp_account': self.bank_account_id.acc_number or '',
            'emp_base_salary': self.contract_id.wage,
            'emp_diary_salary': contract.l10n_mx_edi_integrated_salary,
            'emp_state': self.address_id.state_id.code,
        }

    @api.multi
    def get_working_date(self):
        """Based on employee category, verify if a category set in this
        employee come from this module and get code."""
        category = self.category_ids.filtered(lambda r: r.color == 3)
        if not category:
            return ''  # pragma: no cover
        xml = category[0].get_metadata() and category[0].get_metadata()[0].get(
            'xmlid', False)
        if not xml or xml.split('.')[0] != 'l10n_mx_edi_payslip':
            return ''  # pragma: no cover
        return category[0].name[:2]


class HrContract(models.Model):

    _inherit = "hr.contract"

    l10n_mx_edi_integrated_salary = fields.Float(
        'Integrated Salary', help='Used in the CFDI to express the salary '
        'that is integrated with the payments made in cash by daily quota, '
        'gratuities, perceptions, room, premiums, commissions, benefits in '
        'kind and any other quantity or benefit that is delivered to the '
        'worker by his work, Pursuant to Article 84 of the Federal Labor '
        'Law. (Used to calculate compensation).')
    # Overwrite options & default
    schedule_pay = fields.Selection([
        ('01', 'Daily'),
        ('02', 'Weekly'),
        ('03', 'Fortnightly'),
        ('04', 'Biweekly'),
        ('05', 'Bimonthly'),
        ('06', 'Unit work'),
        ('07', 'Commission'),
        ('08', 'Raised price'),
        ('09', 'Decennial'),
        ('99', 'Other')], default='02')


class HrPayslipOvertime(models.Model):
    _name = 'hr.payslip.overtime'

    name = fields.Char('Description', required=True)
    payslip_id = fields.Many2one(
        'hr.payslip', required=True, ondelete='cascade',
        help='Payslip related.')
    days = fields.Integer(
        help="Number of days in which the employee performed overtime in the "
        "period", required=True)
    hours = fields.Integer(
        help="Number of overtime hours worked in the period", required=True)
    overtime_type = fields.Selection([
        ('01', 'Double'),
        ('02', 'Triples'),
        ('03', 'Simples')], 'Type', required=True, default='01',
        help='Used to express the type of payment of the hours extra.')
    amount = fields.Float(
        help="Amount paid for overtime", required=True, default=0.0)


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    @api.multi
    def _get_perceptions_taxed(self):
        categ_g = self.env.ref(
            'l10n_mx_edi_payslip.hr_salary_rule_category_perception_mx_taxed')
        perceptions = []
        total_g = 0.0
        for line in self.filtered(lambda r: r.category_id == categ_g):
            # Are omitted the perceptions that need other attributes to be
            # added in other process
            # 019 Horas extra
            # 045 Ingresos en acciones o titulos valor que representan bienes
            total_g += line.total
            if line.code[2:] in ['019', '045']:
                continue
            perception = {
                'type': line.code[2:],
                'key': line.code,
                'concept': line.name[:100],
                'amount_g': line.total,
            }
            perceptions.append(perception)
        return perceptions, total_g

    @api.multi
    def _get_perceptions_exempt(self):
        categ_e = self.env.ref(
            'l10n_mx_edi_payslip.hr_salary_rule_category_perception_mx_exempt')
        perceptions = []
        total_e = 0.0
        for line in self.filtered(lambda r: r.category_id == categ_e):
            # Are omitted the perceptions that need other attributes to be
            # added in other process
            # 019 Horas extra
            # 045 Ingresos en acciones o titulos valor que representan bienes
            total_e += line.total
            if line.code[2:] in ['019', '045']:
                continue
            perception = {
                'type': line.code[2:],
                'key': line.code,
                'concept': line.name[:100],
                'amount_e': line.total,
            }
            perceptions.append(perception)
        return perceptions, total_e

    @api.multi
    def _get_extra_lines(self):
        """Some perceptions need other nodes to complete the XML, here are
        added that perceptions with extra data:
            - 019 Horas extra
            - 045 Ingresos en acciones o titulos valor que representan bienes
        """
        categ_g = self.env.ref(
            'l10n_mx_edi_payslip.hr_salary_rule_category_perception_mx_taxed')
        categ_e = self.env.ref(
            'l10n_mx_edi_payslip.hr_salary_rule_category_perception_mx_exempt')
        extra_lines = []
        overtime_ids = self.filtered(lambda r: r.code[2:] == '019')
        payslip = self.mapped('slip_id')
        if overtime_ids:
            extra = [{
                'days': e.days,
                'type': e.overtime_type,
                'amount': e.amount,
                'hours': e.hours
            } for e in payslip.l10n_mx_edi_overtime_line_ids]
            overtime = {
                'type': overtime_ids[0].code[2:],
                'key': overtime_ids[0].code[2:],
                'concept': overtime_ids[0].name,
                'amount_g': overtime_ids.filtered(lambda r: r.category_id == categ_g).total,  # noqa
                'amount_e': overtime_ids.filtered(lambda r: r.category_id == categ_e).total,  # noqa
                'extra_hours': extra,
            }
            extra_lines.append(overtime)
        actions_ids = self.filtered(lambda r: r.code[2:] == '045')
        actions = payslip.l10n_mx_edi_action_title_ids
        for action in actions_ids:
            extra = {
                'value': actions.filtered(
                    lambda r: r.category_id == action.category_id).market_value,  # noqa
                'price': actions.filtered(
                    lambda r: r.category_id == action.category_id).price_granted,  # noqa
            }
            perception = {
                'type': action.code[2:],
                'key': action.code[2:],
                'concept': action.name,
                'amount_g': action.total if action.category_id == categ_g else 0.0,  # noqa
                'amount_e': action.total if action.category_id == categ_e else 0.0,  # noqa
                'action': extra,
            }
            extra_lines.append(perception)
        return extra_lines


class HrPayslipActionTitles(models.Model):
    _name = 'hr.payslip.action.titles'

    payslip_id = fields.Many2one(
        'hr.payslip', required=True, ondelete='cascade',
        help='Payslip related.')
    category_id = fields.Many2one(
        'hr.salary.rule.category', 'Category', required=True,
        help='Indicate to which perception will be added this attributes in '
        'node XML')
    market_value = fields.Float(
        help='When perception type is 045 this value must be assigned in the '
        'line. Will be used in node "AccionesOTitulos" to the attribute '
        '"ValorMercado"', required=True)
    price_granted = fields.Float(
        help='When perception type is 045 this value must be assigned in the '
        'line. Will be used in node "AccionesOTitulos" to the attribute '
        '"PrecioAlOtorgarse"', required=True)


class HrPayslipExtraPerception(models.Model):
    _name = 'hr.payslip.extra.perception'

    payslip_id = fields.Many2one(
        'hr.payslip', required=True, ondelete='cascade',
        help='Payslip related.')
    node = fields.Selection(
        [('retirement', 'JubilacionPensionRetiro'),
         ('separation', 'SeparacionIndemnizacion')], help='Indicate what is '
        'the record purpose, if will be used to add in node '
        '"JubilacionPensionRetiro" or in "SeparacionIndemnizacion"')
    amount_total = fields.Float(
        help='If will be used in the node "JubilacionPensionRetiro" and '
        'will be used to one perception with code "039", will be used to '
        'the attribute "TotalUnaExhibicion", if will be used to one '
        'perception with code "044", will be used to the attribute '
        '"TotalUnaExhibicion". If will be used in the node '
        '"SeparacionIndemnizacion" will be used in attribute "TotalPagado"')
    amount_daily = fields.Float(
        help='Used when will be added in node "JubilacionPensionRetiro", to '
        'be used in attribute "MontoDiario"')
    accumulable_income = fields.Float(
        help='Used to both nodes, each record must be have the valor to each '
        'one.')
    non_accumulable_income = fields.Float(
        help='Used to both nodes, each record must be have the valor to each '
        'one.')
    service_years = fields.Integer(
        help='Used when will be added in node "SeparacionIndemnizacion", to '
        'be used in attribute "NumAñosServicio"')
    last_salary = fields.Float(
        help='Used when will be added in node "SeparacionIndemnizacion", to '
        'be used in attribute "UltimoSueldoMensOrd"')


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    l10n_mx_edi_payment_date = fields.Date(
        'Payment Date', required=True,
        default=time.strftime('%Y-%m-01'), help='Save the payment date that '
        'will be added on all payslip created with this batch.')
