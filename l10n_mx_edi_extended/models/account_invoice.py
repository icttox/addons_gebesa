# Copyright 2020, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from xml.dom import minidom
from codecs import BOM_UTF8
from io import BytesIO
from datetime import datetime
from itertools import groupby
import shutil
import os
import base64
import urllib.request
import logging
from lxml import etree
from lxml.objectify import fromstring
import requests
from ast import literal_eval

from odoo import _, api, fields, models, tools
from odoo.tools import float_round, DEFAULT_SERVER_TIME_FORMAT
from odoo.tools.xml_utils import _check_with_xsd
from odoo.exceptions import UserError

BOM_UTF8U = BOM_UTF8.decode('UTF-8')
CFDI_TEMPLATE = 'l10n_mx_edi.cfdiv32'
CFDI_TEMPLATE_33 = 'l10n_mx_edi.cfdiv33'
CFDI_TEMPLATE_40 = 'l10n_mx_edi_extended.cfdiv40'
CFDI_XSLT_CADENA = 'l10n_mx_edi_extended/data/%s/cadenaoriginal.xslt'

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def create_list_html(array):
    '''Convert an array of string to a html list.
    :param array: A list of strings
    :return: an empty string if not array, an html list otherwise.
    '''
    if not array:
        return ''
    msg = ''
    for item in array:
        msg += '<li>' + item + '</li>'
    return '<ul>' + msg + '</ul>'


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    break_down_disc = fields.Boolean(
        string=_(u"Desglozar descuentos"),
        default=False)
    cfdi_send = fields.Boolean(
        string='CFDI send',
    )
    l10n_mx_edi_usage = fields.Selection([
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
        ('D01', 'Medical, dental and hospital expenses.'),
        ('D02', 'Medical expenses for disability'),
        ('D03', 'Funeral expenses'),
        ('D04', 'Donations'),
        ('D05', 'Real interest effectively paid for mortgage loans (room house)'),
        ('D06', 'Voluntary contributions to SAR'),
        ('D07', 'Medical insurance premiums'),
        ('D08', 'Mandatory School Transportation Expenses'),
        ('D09', 'Deposits in savings accounts, premiums based on pension plans.'),
        ('D10', 'Payments for educational services (Colegiatura)'),
        ('S01', 'No tax effects'),
        ('CP01', 'Payments'),
        ('CN01', 'Payroll'),
        ('P01', 'To define'),
    ], 'Usage', default='G01',
        help='Used in CFDI 4.0 to express the key to the usage that will '
        'gives the receiver to this invoice. This value is defined by the '
        'customer. \nNote: It is not cause for cancellation if the key set is '
        'not the usage that will give the receiver of the document.')
    not_sing_invoice_refund = fields.Boolean(
        string='No timbrar NC',
    )
    rate_mex = fields.Float(
        string='Tipo de cambio',
        help='Paridad utilizada en la fecha de la factura',
        compute='_compute_rate_mex',
    )
    l10n_mx_edi_export = fields.Selection([
        ('01', 'No aplica'),
        ('02', 'Definitiva'),
        ('03', 'Temporal'),
    ], string='Exportacion',
        compute='_compute_l10n_mx_edi_export',)

    xml_intermediate = fields.Text(
        string='XML Intermediate',
        help='XML Intermediate',
    )
    l10n_mx_edi_reason_cancellation = fields.Selection(
        [('01', 'Comprobante emitido con errores con relacion'),
         ('02', 'Comprobante emitido con errores sin relacion'),
         ('03', 'No se llevo a cabo la operación'),
         ('04', 'Operación nominativa relacionada en la factura global')],
        string='Motivo de cancelacion',
        copy=False,
    )
    l10n_mx_edi_invoices_replace = fields.Char(
        string='UUID que remplazan',
        copy=False,
    )
    l10n_mx_edi_periodicity = fields.Selection([
        ('01', 'Diario'),
        ('02', 'Semanal'),
        ('03', 'Quincenal'),
        ('04', 'Mensual'),
        ('05', 'Bimestral')],
        string='Periodicidad',
        default=False)
    l10n_mx_edi_month = fields.Selection([
        ('01', 'Enero'),
        ('02', 'Febrero'),
        ('03', 'Marzo'),
        ('04', 'Abril'),
        ('05', 'Mayo'),
        ('06', 'Junio'),
        ('07', 'Julio'),
        ('08', 'Agosto'),
        ('09', 'Septiembre'),
        ('10', 'Octubre'),
        ('11', 'Noviembre'),
        ('12', 'Diciembre'),
        ('13', 'Enero-Febrero'),
        ('14', 'Marzo-Abril'),
        ('15', 'Mayo-Junio'),
        ('16', 'Julio-Agosto'),
        ('17', 'Septiembre-Octubre'),
        ('18', 'Noviembre-Diciembre')],
        string='Mes',
        default=False)
    l10n_mx_edi_year = fields.Integer(
        string='Año',
        default=False
    )

    @api.multi
    @api.depends('currency_id', 'date_invoice')
    def _compute_rate_mex(self):
        for inv in self:
            date = inv.date_invoice or fields.Date.today()
            query = """
                SELECT r.rate_mex FROM res_currency_rate r
                WHERE r.currency_id = %s AND r.name <= %s
                    AND (r.company_id IS NULL OR r.company_id = %s)
                ORDER BY r.company_id, r.name DESC LIMIT 1"""
            self._cr.execute(query, (inv.currency_id.id, date, inv.company_id.id))
            currency_rates = self._cr.fetchall()
            if currency_rates:
                inv.rate_mex = currency_rates[0][0]
            else:
                inv.rate_mex = 1

    def _compute_l10n_mx_edi_export(self):
        for inv in self:
            self.l10n_mx_edi_export = '01'

    @api.model
    def l10n_mx_edi_get_customer_rfc(self):
        if all(line.product_id.l10n_mx_edi_transfer is True for line in self.invoice_line_ids):
            return 'XAXX010101000'
        partner_id = self.partner_id
        if self.partner_id.type != 'invoice':
            partner_id = self.partner_id.commercial_partner_id
        return partner_id.l10n_mx_edi_get_customer_rfc()

    @api.multi
    def l10n_mx_edi_is_required(self):
        if self.not_sing_invoice_refund is True and self.type == 'out_refund':
            return False
        return super().l10n_mx_edi_is_required()

    @api.model
    def create(self, vals_list):
        if 'partner_id' not in vals_list:
            return super().create(vals_list)
        partner = self.env['res.partner'].browse(vals_list['partner_id'])
        mp_id = self.env['l10n_mx_edi.payment.method'].search([('code', '=', '99')], limit=1)
        vals_list['l10n_mx_edi_usage'] = partner.l10n_mx_edi_usage or 'G01'
        vals_list['l10n_mx_edi_payment_method_id'] = partner.l10n_mx_edi_payment_method_id.id or vals_list.get('l10n_mx_edi_payment_method_id', False) or mp_id.id
        return super().create(vals_list)

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        """Inherit to set account_payment, use cfdi and payment method assigned
        in the partner."""
        res = super()._onchange_partner_id()
        use_cfdi = self.commercial_partner_id.l10n_mx_edi_usage
        method_cfdi = self.commercial_partner_id.l10n_mx_edi_payment_method_id.id
        self.l10n_mx_edi_usage = use_cfdi or self.l10n_mx_edi_usage
        self.l10n_mx_edi_payment_method_id = method_cfdi or self.l10n_mx_edi_payment_method_id.id
        self.l10n_mx_edi_export = '01'
        if self.partner_id.country_id != self.env.ref('base.mx'):
            self.l10n_mx_edi_export = '02'
        return res

    @api.multi
    def _perform_l10n_mx_validations(self):

        for inv in self.filtered(lambda r: r.l10n_mx_edi_is_required()):
            xml_inter = self.search([
                ('xml_intermediate', '!=', False), ('id', '!=', inv.id),
                ('state', '=', 'draft')])
            if xml_inter:
                raise UserError(
                    'Servicio de timbrado en pausa, favor inténtalo de nuevo en 10 minutos.')
            if not inv.l10n_mx_edi_usage:
                raise UserError(_(
                    'This invoice have not an Usage Cfdi defined.'))

            if inv.l10n_mx_edi_external_trade and not inv.l10n_mx_edi_incoterm:
                raise UserError(_(
                    'This invoice have not an Incoterm defined.'))

            # if not inv.company_id.partner_id.l10n_mx_edi_name:
            #     raise UserError(_(
            #         'The Company\'s partner have not a name for the cfdi.'))

            if not inv.company_id.partner_id.city_id:
                raise UserError(_(
                    'The Company\'s partner have not a City defined.'))

            if not inv.company_id.partner_id.state_id:
                raise UserError(_(
                    'The Company\'s partner have not a State defined.'))

            if not inv.company_id.partner_id.country_id:
                raise UserError(_(
                    'The Company\'s partner have not a Country defined.'))

            if not inv.company_id.partner_id.zip:
                raise UserError(_(
                    'The Company\'s partner have not a ZIP defined.'))

            # if not inv.partner_id.l10n_mx_edi_name:
            #     raise UserError(_(
            #         'Partner have not name for cfdi. Please set that value.'))

            if not inv.partner_id.email:
                raise UserError(_(
                    'Partner have not email. Please set that value.'))

            if not inv.partner_id.commercial_partner_id.property_account_position_id.l10n_mx_edi_code:
                raise UserError(_(
                    'Partner have not tax regime. Please set that value.'))

            if not inv.payment_term_id:
                raise UserError(_(
                    'Invoice have not payment term. Please set that value.'))

            if inv.partner_id.type != 'invoice' and\
                    inv.partner_id.commercial_partner_id.type != 'invoice':
                raise UserError(_(
                    'The partner and the commercial partner '
                    'of the CFDI, are not a billing address.'))

            if not inv.company_id.partner_id.property_account_position_id:
                raise UserError(_(
                    'The Company\'s partner have not an Account Position defined.'))

            if not inv.company_id.partner_id.property_account_position_id.l10n_mx_edi_code:
                raise UserError(_(
                    'The Company\'s partner Account position have not a Code defined.'))

            if not inv.journal_id.l10n_mx_address_issued_id:
                raise UserError(_(
                    'The journal related to this invoice have not an emmission address.'))

            if inv.currency_id.id != inv.partner_id.property_product_pricelist.currency_id.id:
                raise UserError(_(
                    'Customer has not a pricelist in: %s') % inv.currency_id.name)

            for invline in inv.invoice_line_ids:
                if not invline.product_id.l10n_mx_edi_code_sat_id:
                    raise UserError(_(
                        'This product has not a SAT Cfdi classification: %s.') % invline.product_id.default_code)

                if inv.l10n_mx_edi_external_trade and not invline.product_id.l10n_mx_edi_tariff_fraction_id:
                    raise UserError(_(
                        'This product has not a Tariff Fraction defined: %s') % invline.product_id.default_code)

                if inv.l10n_mx_edi_external_trade and not invline.product_id.l10n_mx_edi_umt_aduana_id:
                    raise UserError(_(
                        'This product has not an UMT Aduana defined, %s') % invline.product_id.default_code)

            for taxline in inv.tax_line_ids:
                if not taxline.tax_id.l10n_mx_cfdi_tax_type:
                    raise UserError(_(
                        'This tax has not a Factor Type defined'))

                if not taxline.tax_id.tag_ids:
                    # las etiquetas de impuesto en los impuestos deben ser IVA o ISR no mas
                    raise UserError(_(
                        'This tax has not a Tag defined'))

    @api.multi
    def _l10n_mx_edi_get_payment_policy(self):
        self.ensure_one()
        version = self.l10n_mx_edi_get_pac_version()
        term_ids = self.payment_term_id.line_ids
        dias = self.payment_term_id.line_ids[0].days
        if version == '3.2':
            if len(term_ids.ids) > 1:
                return 'Pago en parcialidades'
            return 'Pago en una sola exhibición'
        if version == '3.3' and self.date_due and self.date_invoice:
            if self.type == 'out_refund':
                return 'PUE'
            # In CFDI 3.3 - SAT 2018 rule 2.7.1.44, the payment policy is PUE
            # if the invoice will be paid before 17th of the following month,
            # PPD otherwise
            # date_pue = (fields.Date.from_string(self.date_invoice) +
            #             relativedelta(day=17, months=1))
            # date_due = fields.Date.from_string(self.date_due)
            if dias > 1:
                # if (date_due > date_pue or len(term_ids) > 1):
                return 'PPD'
            return 'PUE'
        elif version == '4.0' and self.date_due and self.date_invoice:
            if self.type == 'out_refund':
                return 'PUE'
            # In CFDI 3.3 - SAT 2018 rule 2.7.1.44, the payment policy is PUE
            # if the invoice will be paid before 17th of the following month,
            # PPD otherwise
            if (dias > 1):
                return 'PPD'
            return 'PUE'
        return ''

    @api.multi
    def get_cfdi_related(self):
        """To node CfdiRelacionados get documents related with each invoice
        from l10n_mx_edi_origin, hope the next structure:
            relation type|UUIDs separated by ,"""
        self.ensure_one()
        if self.l10n_mx_edi_get_pac_version() == '3.3':
            return super().get_cfdi_related()

        related = {}
        if self.l10n_mx_edi_origin:
            types = self.l10n_mx_edi_origin.split(';')
            for typ in types:
                origin = typ.split('|')
                uuids = origin[1].split(',') if len(origin) > 1 else []
                related[origin[0]] = [u.strip() for u in uuids]
        return related

    @api.multi
    def invoice_validate(self):
        '''Generates the cfdi attachments for mexican companies when validated.'''
        self._perform_l10n_mx_validations()
        result = super().invoice_validate()
        # for record in self.filtered(lambda r: r.l10n_mx_edi_is_required()):
        #     pdf = record.attachment_invoice_pdf()
        #     record.send_email_invoice(pdf=pdf)
        return result

    def attachment_invoice_pdf(self):
        """ Sign the xml file
        """
        attachment = self.env['ir.attachment']
        namepdf = ('%s-MX-Invoice-10.pdf' % (
            self.number))

        attachment_id = attachment.search([
            ('name', '=', namepdf),
            ('res_model', '=', 'account.invoice'),
            ('res_id', '=', self.id)], limit=1)

        if not attachment_id:
            report = self.env['ir.actions.report']._get_report_from_name(
                'account.report_invoice')
            pdf = report.render_qweb_pdf(self.id)[0]

            data_attach = {
                'name': namepdf,
                'datas': base64.encodestring(pdf or ''),
                'datas_fname': self.company_id.vat + '_' + self.number + '.pdf',
                'res_model': 'account.invoice',
                'res_id': self.id,
            }
            attachment_id = attachment.create(data_attach)
        return attachment_id

    @api.model
    def l10n_mx_edi_get_xml_etree(self, cfdi=None):
        '''Get an objectified tree representing the cfdi.
        If the cfdi is not specified, retrieve it from the attachment.

        :param cfdi: The cfdi as string
        :return: An objectified tree
        '''
        # TODO helper which is not of too much help and should be removed
        self.ensure_one()
        if cfdi is None and self.l10n_mx_edi_cfdi:
            cfdi = base64.decodestring(self.l10n_mx_edi_cfdi)
        if cfdi is None and self.xml_signed:
            cfdi = self.xml_signed.encode()
        if cfdi:
            cfdi = cfdi.replace(b'A&#241;o', b'A\xc3\xb1o')
        return fromstring(cfdi) if cfdi else None

    def send_email_invoice(self):
        subject = 'Error when try send invoice by email'
        body = '<h2>Error when try send invoice by email</h2>'
        body = body + '<hr/>Partner have not email. Please set that value.'
        for record in self:
            if not record.partner_id.email:
                msg_error = record.message_ids.filtered(
                    lambda msg: msg.subject == subject and msg.body == body)
                if not msg_error:
                    record.message_post(subject=subject, body=body)
                continue

            tmp = self.env.ref('account.email_template_edi_invoice', False)

            pdf = record.attachment_invoice_pdf()
            attachments = [(6, 0, [pdf.id])]

            mail = self.env['mail.compose.message'].with_context(
                dict(
                    default_model='account.invoice',
                    default_res_id=self.id,
                    default_use_template=bool(tmp),
                    default_template_id=tmp.id,
                    default_composition_mode='mass_mail',
                    mark_invoice_as_sent=True,
                )).create({})
            data = {}
            errored = False
            try:
                data = mail.onchange_template_id(
                    tmp.id, None, 'account.invoice', record.id).get(
                        'value', {})
            except BaseException as exc:
                _logger.info("invoice not sent even if configured. %s")
                data.update({'subject': str(exc)})
                errored = True
            mail.write({
                'body': data.get('body', 'invoice not sent because an '
                                         'error rendering or generating '
                                         'the email'),
                # 'partner_ids': data.get('partner_ids', []),
                'email_from': data.get('email_from', 'noreply@gebesa.com'),
                'attachment_ids': attachments,
                # 'attachment_ids': data.get('attachment_ids', []),
                'subject': data.get('subject', ''),
            })

            mail.with_context(mark_invoice_as_sent=True).send_mail()
            mail = self.env['mail.mail'].search([
                ('res_id', '=', record.id),
                ('model', '=', 'account.invoice'),
                ('subject', '=', data.get('subject', ''))], limit=1)
            if not mail and not errored:
                # record.cfdi_send = True
                query = """
                    UPDATE account_invoice SET cfdi_send = True
                    WHERE id = %s
                """ % record.id
                self.env.cr.execute(query)
                continue
            # record.write({'sent': False})
            record.message_post(
                subject=subject,
                body='<br>'.join(["- " + msg.failure_reason for msg in mail
                                  if msg.failure_reason]))

    @api.multi
    def button_payment(self):
        return {
            'name': _('Payments'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('invoice_ids', 'in', self.ids)],
        }

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        """ Prepare the dict of values to create the new credit note from the invoice.
            This method may be overridden to implement custom
            credit note generation (making sure to call super() to establish
            a clean extension chain).

            :param record invoice: invoice as credit note
            :param string date_invoice: credit note creation date from the wizard
            :param integer date: force date from the wizard
            :param string description: description of the credit note from the wizard
            :param integer journal_id: account.journal from the wizard
            :return: dict of value to create() the credit note
        """
        values = super()._prepare_refund(
            invoice, date_invoice, date, description, journal_id)
        mode = self._context.get('mode', False)
        if invoice.l10n_mx_edi_cfdi_uuid:
            typerel = '01' if mode == 'refund' else '03'
            if typerel == '01':
                deposit = literal_eval(self.env[
                    'ir.config_parameter'].sudo().get_param(
                        'sale.default_deposit_product_id', 'False'))
                if values['invoice_line_ids'][0][2]['product_id'] == deposit:
                    typerel = '07'
            values['l10n_mx_edi_origin'] = typerel + '|' + invoice.l10n_mx_edi_cfdi_uuid
        return values

    @api.multi
    def _l10n_mx_edi_call_service(self, service_type):
        '''Call the right method according to the pac_name, it's info returned by the '_l10n_mx_edi_%s_info' % pac_name'
        method and the service_type passed as parameter.
        :param service_type: sign or cancel
        '''
        # Regroup the invoices by company (= by pac)
        comp_x_records = groupby(self, lambda r: r.company_id)
        for company_id, records in comp_x_records:
            pac_name = company_id.l10n_mx_edi_pac
            if not pac_name:
                continue
            # Get the informations about the pac
            pac_info_func = '_l10n_mx_edi_%s_info' % pac_name
            service_func = '_l10n_mx_edi_%s_%s' % (pac_name, service_type)
            pac_info = getattr(self, pac_info_func)(company_id, service_type)
            # Call the service with invoices one by one or all together according to the 'multi' value.
            multi = pac_info.pop('multi', False)
            if multi:
                # rebuild the recordset
                records = self.env['account.invoice'].search(
                    [('id', 'in', self.ids), ('company_id', '=', company_id.id)])
                getattr(records, service_func)(pac_info)
            else:
                for record in records:
                    getattr(record, service_func)(pac_info)

    @api.multi
    def _l10n_mx_edi_create_downpayments_cfdi_values(self):
        '''Create the downpayments values to fill the CFDI template.
        '''
        prepayment = 0
        for line in self.invoice_line_ids.filtered(lambda r: r.quantity < 1):
            prepayment += abs(line.price_subtotal)

        return prepayment

    @api.multi
    def _l10n_mx_edi_create_taxes_cfdi_values(self):
        '''Create the taxes values to fill the CFDI template.
        '''
        self.ensure_one()
        values = {
            'total_withhold': 0,
            'total_transferred': 0,
            'withholding': [],
            'transferred': [],
        }
        taxes = {}
        descuentos = subtotal = cou_lin = 0
        for line in self.invoice_line_ids:
            if line.price_subtotal < 0:
                descuentos += abs(round(line.price_subtotal, 2))
            else:
                subtotal += abs(round(line.price_subtotal, 2))
                cou_lin += 1
        mcontrol = descuentos
        # for line in self.invoice_line_ids.filtered('price_subtotal'):
        for line in self.invoice_line_ids.filtered(lambda lin: lin.quantity > 0):
            cou_lin -= 1
            discount = 0
            if descuentos > 0:
                if cou_lin != 0:
                    line_subtotal = round((round(line.price_subtotal, 2) * 100), 2)
                    factor = (round((line_subtotal / round(subtotal, 2)), 2) / 100)
                    discount = round(abs(factor * descuentos), 2)
                    mcontrol -= discount
                else:
                    discount = mcontrol

            price = (line.price_unit * (1.0 - (line.discount or 0.0) / 100.0)) - (discount / line.quantity)
            # price = line.price_unit * (1.0 - (line.discount or 0.0) / 100.0)
            taxes_line = line.invoice_line_tax_ids
            taxes_line = taxes_line.filtered(
                lambda tax: tax.amount_type != 'group') + taxes_line.filtered(
                    lambda tax: tax.amount_type == 'group').mapped(
                        'children_tax_ids')
            tax_line = {tax['id']: tax for tax in taxes_line.compute_all(
                price, line.currency_id, line.quantity, line.product_id, line.partner_id)['taxes']}
            for tax in taxes_line.filtered(lambda r: r.l10n_mx_cfdi_tax_type != 'Exento'):
                tax_dict = tax_line.get(tax.id, {})
                # amount = round(abs(tax_dict.get(
                #     'amount', tax.amount / 100 * float("%.2f" % line.price_subtotal))), 2)

                amount = round(tax_dict.get(
                    'amount', tax.amount / 100 * float("%.2f" % line.price_subtotal)), 2)
                # _logger.info(str(amount))

                # if not self.break_down_disc:
                #     amount = round((tax.amount / 100 * float("%.2f" % (
                #         line.price_unit * line.quantity))), 2)

                name_tax = (tax.tag_ids[0].name if tax.tag_ids else tax.name).upper()

                taxiave = 'tras-' + name_tax + '-' +\
                    tax.l10n_mx_cfdi_tax_type + '-' +\
                    str(round(abs(tax.amount), 2))

                if tax.retaining:
                    amount = abs(amount)
                    taxiave = 'ret-' + name_tax

                rate = round(abs(tax.amount), 2)
                if taxiave not in taxes:
                    taxes.update({taxiave: {
                        'name': name_tax,
                        'amount': amount,
                        'base': 0.01 if amount <= 0.00 and descuentos > 0.00 else round(price * line.quantity, 2) if descuentos > 0.00 else round(line.price_subtotal, 2),
                        'rate': rate if tax.amount_type == 'fixed' else rate / 100.0,
                        'type': tax.l10n_mx_cfdi_tax_type,
                        'tax_amount': tax_dict.get('amount', tax.amount),
                        'retaining': tax.retaining,
                    }})
                else:
                    taxes[taxiave].update({
                        'amount': taxes[taxiave]['amount'] + amount,
                        'base': taxes[taxiave]['base'] + (0.01 if amount <= 0.00 and descuentos > 0.00 else round(price * line.quantity, 2) if descuentos > 0.00 else round(line.price_subtotal, 2)),
                    })

                if tax.retaining:
                    values['total_withhold'] += amount
                else:
                    values['total_transferred'] += amount

        values['transferred'] = [tax for tax in taxes.values() if not tax['retaining']]
        values['withholding'] = [tax for tax in taxes.values() if tax['retaining']]
        return values

    @api.multi
    def _get_report_extra_data(self):
        """Method used to get the extra data that is not found in the XML,
        but is used in the report."""
        self.ensure_one()
        sale_names = '\n'.join(self.invoice_line_ids.mapped('sale_line_ids')
                               .mapped('order_id').mapped('name')) \
            if hasattr(self.invoice_line_ids, 'invoice_line_ids') else ''
        return {
            'reference': self.name or '',
            'origin': self.origin or '',
            'sale_order_name': sale_names,
        }

    @api.multi
    def _l10n_mx_edi_create_cfdi_values(self):
        '''Create the values to fill the CFDI template.
        '''
        self.ensure_one()
        precision_digits = self.env['decimal.precision'].precision_get('Account')
        partner_id = self.partner_id
        if self.partner_id.type != 'invoice':
            partner_id = self.partner_id.commercial_partner_id
            self.message_post(body=_(
                'The business partner address was used for the generation of '
                'the CFDI, since the customer address is not a billing address.'),
                subtype='account.mt_invoice_validated')

        if not self.company_id.partner_id.commercial_partner_id.l10n_mx_edi_name:
            self.company_id.partner_id.commercial_partner_id._l10n_mx_edi_clean_to_legal_name()
        if not partner_id.commercial_partner_id.l10n_mx_edi_name:
            partner_id.commercial_partner_id._l10n_mx_edi_clean_to_legal_name()
        values = {
            'record': self,
            'currency_name': self.currency_id.name,
            'supplier': self.company_id.partner_id.commercial_partner_id,
            'issued': self.journal_id.l10n_mx_address_issued_id,
            'customer': partner_id,
            'fiscal_position': self.company_id.partner_id.property_account_position_id,
            'payment_method': self.l10n_mx_edi_payment_method_id.code,
            'use_cfdi': self.l10n_mx_edi_usage,
            'conditions': self._get_string_cfdi(
                self.payment_term_id.name, 1000) if self.payment_term_id else False,
            'invoice_line_ids': self.invoice_line_ids,
        }

        values.update(self._l10n_mx_get_serie_and_folio(self.number))
        ctx = dict(company_id=self.company_id.id, date=self.date_invoice)
        mxn = self.env.ref('base.MXN').with_context(ctx)
        invoice_currency = self.currency_id.with_context(ctx)
        values['rate'] = ('%.6f' % (invoice_currency.compute(1, mxn, round=False))) if self.currency_id.name != 'MXN' else False

        if self.type == 'out_invoice':
            if all(line.product_id.l10n_mx_edi_transfer for line in self.invoice_line_ids):
                values['document_type'] = 'traslado'
                values['currency_name'] = 'XXX'
            else:
                values['document_type'] = 'ingreso'
        else:
            values['document_type'] = 'egreso'
        values['payment_policy'] = self._l10n_mx_edi_get_payment_policy()
        domicile = self.journal_id.l10n_mx_address_issued_id or self.company_id
        values['domicile'] = '%s %s, %s' % (
            domicile.city,
            domicile.state_id.name,
            domicile.country_id.name,
        )

        values['downpayments'] = self._l10n_mx_edi_create_downpayments_cfdi_values()
        values['decimal_precision'] = precision_digits
        subtotal_wo_discount = lambda l: float_round(
            l.price_subtotal / (1 - l.discount / 100) if l.discount != 100 else
            l.price_unit * l.quantity, 2)

        # if not self.break_down_disc:

        values['subtotal_wo_discount'] = subtotal_wo_discount
        get_discount = lambda l, d: ('%.*f' % (
            int(d), subtotal_wo_discount(l) - l.price_subtotal)) if l.discount else False
        values['total_discount'] = get_discount
        total_discount = sum([float(get_discount(p, precision_digits)) for p in self.invoice_line_ids])
        # Para cfdi por remanente de anticipo
        total_discount += float(values['downpayments'] or 0)
        values['amount_untaxed'] = '%.*f' % (
            precision_digits, sum(
                [subtotal_wo_discount(p) for p in self.invoice_line_ids]) + float(values['downpayments'] or 0))

        values['amount_discount'] = '%.*f' % (precision_digits, total_discount) if total_discount else None
        # Tratar descuentos como parte del precio
        # para no generar cfdis con descuentos reales
        if not self.break_down_disc and values['amount_discount'] and not values['downpayments']:
            values['amount_untaxed'] = float(values['amount_untaxed']) - float(values['amount_discount'])
            values['amount_discount'] = '0.00'
            get_discount_zero = lambda l, d: (
                '%.*f' % (int(d), 0.00)) if l.discount else False
            values['total_discount'] = get_discount_zero

            subtotal_wo_discount = lambda l: float_round(
                l.price_subtotal, int(precision_digits))
            values['subtotal_wo_discount'] = subtotal_wo_discount

        if not values['amount_discount']:
            values['amount_discount'] = '0.00'

        values['taxes'] = self._l10n_mx_edi_create_taxes_cfdi_values()

        values['amount_total'] = '%0.*f' % (
            precision_digits,
            float(values['amount_untaxed']) - float(values['amount_discount'] or 0) + (
                values['taxes']['total_transferred'] or 0) - (
                values['taxes']['total_withhold'] or 0))

        values['tax_name'] = lambda t: {'ISR': '001', 'IVA': '002', 'IEPS': '003'}.get(
            t, False)

        if self.l10n_mx_edi_partner_bank_id:
            digits = [s for s in self.l10n_mx_edi_partner_bank_id.acc_number if s.isdigit()]
            acc_4number = ''.join(digits)[-4:]
            values['account_4num'] = acc_4number if len(acc_4number) == 4 else None
        else:
            values['account_4num'] = None

        return values

    @api.multi
    def _l10n_mx_edi_render_replace_cfdi(self, template, values):
        cfdi = self.env['ir.qweb'].render(template, values=values)

        cfdi = cfdi.replace(b'xmlns__', b'xmlns:')
        cfdi = cfdi.replace(
            b'\n            <cfdi:Comprobante',
            b'<?xml version="1.0" encoding="UTF-8"?><cfdi:Comprobante')

        return cfdi

    @api.multi
    def _l10n_mx_edi_create_cfdi(self):
        '''Creates and returns a dictionnary containing 'cfdi' if the cfdi is well created, 'error' otherwise.
        '''
        self.ensure_one()
        qweb = self.env['ir.qweb']
        error_log = []
        company_id = self.company_id
        pac_name = company_id.l10n_mx_edi_pac
        values = self._l10n_mx_edi_create_cfdi_values()

        # -----------------------
        # Check the configuration
        # -----------------------
        # -Check certificate
        certificate_ids = company_id.l10n_mx_edi_certificate_ids
        certificate_id = certificate_ids.sudo().get_valid_certificate()
        if not certificate_id:
            error_log.append(_('No valid certificate found'))

        # -Check PAC
        if pac_name:
            pac_test_env = company_id.l10n_mx_edi_pac_test_env
            pac_password = company_id.l10n_mx_edi_pac_password
            if not pac_test_env and not pac_password:
                error_log.append(_('No PAC credentials specified.'))
        else:
            error_log.append(_('No PAC specified.'))

        if error_log:
            raise UserError(_(
                'Please check your configuration: ') + create_list_html(
                error_log))
            # return {'error': _('Please check your configuration: ') + create_list_html(error_log)}

        # -Compute date and time of the invoice
        time_invoice = datetime.strptime(
            self.l10n_mx_edi_time_invoice, DEFAULT_SERVER_TIME_FORMAT).time()
        # -----------------------
        # Create the EDI document
        # -----------------------
        version = self.l10n_mx_edi_get_pac_version()

        # -Compute certificate data
        values['date'] = datetime.combine(
            fields.Datetime.from_string(
                self.date_invoice), time_invoice).strftime('%Y-%m-%dT%H:%M:%S')
        values['certificate_number'] = certificate_id.serial_number
        values['certificate'] = certificate_id.sudo().get_data()[0]

        # -Compute cfdi
        if version == '3.2':
            cfdi = qweb.render(CFDI_TEMPLATE, values=values)
            node_sello = 'sello'
            with tools.file_open(
                    'l10n_mx_edi/data/%s/cfdi.xsd' % version, 'rb') as xsd:
                xsd_datas = xsd.read()
        elif version == '3.3':
            cfdi = self._l10n_mx_edi_render_replace_cfdi(CFDI_TEMPLATE_33, values)
            node_sello = 'Sello'
            attachment = self.env.ref('l10n_mx_edi.xsd_cached_cfdv33_xsd', False)
            xsd_datas = base64.b64decode(attachment.datas) if attachment else b''
        elif version == '4.0':
            cfdi = self._l10n_mx_edi_render_replace_cfdi(CFDI_TEMPLATE_40, values)

            node_sello = 'Sello'
            attachment = self.env.ref('l10n_mx_edi.xsd_cached_cfdv40_xsd', False)
            xsd_datas = base64.b64decode(attachment.datas) if attachment else b''
        else:
            raise UserError(_('Unsupported version %s') % version)
            # return {'error': _('Unsupported version %s') % version}

        # Create xml file w/o seal
        sign_mode = self._context.get('sign_mode', False)
        if sign_mode and sign_mode == 'step-by-step':
            # cfdi_to_file = cfdi.decode('UTF-8')
            fname = "cfdi_tmp_" + str(self.id) + ".dat"
            path = os.path.realpath(
                os.path.join(
                    os.path.dirname(__file__),
                    '..',
                    'bin'))
            # create directory and remove its content
            if not os.path.exists(path):
                os.makedirs(path)
            else:
                # os.chmod(attachment_dir, stat.S_IWUSR)
                shutil.rmtree(path)
                os.makedirs(path)
            fpath = os.path.join(path, fname)
            file = open(fpath, "wb")
            file.write(cfdi)
            file.close()
            raise UserError(_('step-by-step Executed %s') % fname)

        if self.xml_intermediate:
            cfdi = self.xml_intermediate.encode()

        # -Compute cadena
        tree = self.l10n_mx_edi_get_xml_etree(cfdi)
        cadena = self.l10n_mx_edi_generate_cadena(
            CFDI_XSLT_CADENA % version, tree)
        tree.attrib[node_sello] = certificate_id.sudo().get_encrypted_cadena(
            cadena)

        # Check with xsd
        if xsd_datas:
            try:
                with BytesIO(xsd_datas) as xsd:
                    _check_with_xsd(tree, xsd)
            except (IOError, ValueError):
                _logger.info(
                    _('The xsd file to validate the XML structure was not found'))
            except Exception as exc:
                raise UserError(_('The cfdi generated is not valid') +
                                create_list_html(str(exc).split('\\n')))
                # return {'error': (
                #    _('The cfdi generated is not valid') +
                #    create_list_html(str(exc).split('\\n')))}

        res = {'cfdi': b'<?xml version="1.0" encoding="UTF-8"?>' + etree.tostring(tree)}
        return res

    @api.multi
    def action_intermediate_xml(self):
        self.ensure_one()
        ctx = self.env.context.copy()
        ctx.update({'sign_mode': 'step-by-step'})
        self.with_context(ctx).action_invoice_open()

    @api.multi
    def action_read_intermediate_file(self):
        self.ensure_one()
        fname = "cfdi_tmp_" + str(self.id) + ".dat"
        path = os.path.realpath(
            os.path.join(
                os.path.dirname(__file__),
                '..',
                'bin'))

        fpath = os.path.join(path, fname)
        if os.path.isfile(fpath):
            with open(fpath, 'r') as file:
                self.xml_intermediate = file.read().replace('\n', '')
        else:
            raise UserError(_('File not exists %s') % fpath)

    @api.multi
    def cancel_xml_mx(self):
        for record in self.filtered(lambda r: r.l10n_mx_edi_is_required()):
            so_w_advnc = self.env['sale.order'].search([('advance_ids', 'in', record.id)])
            if so_w_advnc:
                raise UserError(
                    'Esta factura se encuentra referenciada en el pedido %s, como anticipo manual, por favor primero quite la referencia a este anticipo del pedido' % so_w_advnc[0].name)
            inv_w_advnc = self.env['account.invoice'].search([('advance_ids', 'in', record.id)])
            if inv_w_advnc:
                raise UserError(
                    'Esta factura se encuentra referenciada en la factura %s, como anticipo manual, por favor primero quite la referencia a este anticipo de la factura' % inv_w_advnc[0].number)
            record._l10n_mx_edi_cancel()

    # -------------------------------------------------------------------------
    # SAT/PAC service methods
    # -------------------------------------------------------------------------

    @api.model
    def _l10n_mx_edi_comdig_info(self, company_id, service_type):
        test = company_id.l10n_mx_edi_pac_test_env
        username = company_id.l10n_mx_edi_pac_username
        password = company_id.l10n_mx_edi_pac_password
        version = self.l10n_mx_edi_get_pac_version()
        if service_type == 'sign':
            if version == '3.3':
                url = 'https://pruebas.comercio-digital.mx/timbre/timbrarV5.aspx'\
                    if test else 'https://ws.comercio-digital.mx/timbre/timbrarV5.aspx'
            else:
                url = 'https://pruebas.comercio-digital.mx/timbre4/timbrarV5'\
                    if test else 'https://ws.comercio-digital.mx/timbre4/timbrarV5'
        elif service_type == 'cancel':
            url = 'https://pruebas.comercio-digital.mx/cancela4/cancelarUuid'\
                if test else 'https://cancela.comercio-digital.mx/cancela4/cancelarUuid'
        elif service_type == 'check':
            url = 'https://cancela.comercio-digital.mx/arws/consultaEstatus'
        else:
            raise UserError(_('Invalid given service type for Comercio Digital'))
        return {
            'url': url,
            'multi': False,  # TODO: implement multi
            'username': 'AAA010101AAA' if test else username,
            'password': 'PWD' if test else password,
        }

    @api.multi
    def _l10n_mx_edi_comdig_sign(self, pac_info):
        '''SIGN for Comercio Digital.
        '''
        url = pac_info['url']
        username = pac_info['username']
        password = pac_info['password']

        for inv in self:
            cfdi = base64.b64decode(inv.l10n_mx_edi_cfdi).decode('UTF-8').replace('A&#241;o', 'A\xc3\xb1o')

            # cfdi = cfdi.replace("<?xml version=\'1.0\' encoding=\'UTF-8\'?>", '')
            # cfdi = '<?xml version="1.0" encoding="UTF-8"?>' + cfdi
            headers = {
                'Content-Type': 'text/xml',
                'usrws': username,
                'pwdws': password}
            try:
                # client = Client(url, timeout=20)
                # response = client.service.stamp(cfdi, headers=headers)

                response = requests.request(
                    'POST', url, data=cfdi, headers=headers, verify=False)
            except Exception as exc:
                err = exc + ' xml: ' + cfdi
                inv.l10n_mx_edi_log_error(str(err))
                continue
            # res = _(tools.ustr(response.text))
            code = _(tools.ustr(response.headers['codigo']))
            msg = ''
            if code and\
               code != '000':
                msg = _(tools.ustr(response.headers['errmsg']))
                msg = msg + ' xml: ' + cfdi

            xml_signed = response.content.decode('UTF-8')

            if xml_signed:
                xml_signed = base64.b64encode(xml_signed.encode('utf-8'))

            inv._l10n_mx_edi_post_sign_process(
                xml_signed if xml_signed else None, code, msg)

    @api.multi
    def _l10n_mx_edi_comdig_cancel(self, pac_info):
        '''CANCEL for Comercio digital.
        '''
        url = pac_info['url']
        username = pac_info['username']
        password = pac_info['password']
        cadenacancela1 = "RFCE={0}\nUSER={1}\nPWDW={2}\nUUID={3}\nCERT={4}"
        cadenacancela2 = "\nRFCR={5}\nTIPOC={6}\nTOTAL={7}\nEMAILE={8}\nEMAILR={9}"
        cadenacancela3 = "\nKEYF={10}\nPWDK={11}\nACUS=SI\nTIPO1=cfdi\nMOTIVO={12}"
        cadenacancela = cadenacancela1 + cadenacancela2 + cadenacancela3
        # http = urllib.request.build_opener(
        #     urllib.request.ProxyHandler, urllib.request.UnknownHandler,
        #     urllib.request.HTTPHandler, urllib.request.HTTPDefaultErrorHandler,
        #     urllib.request.FTPHandler, urllib.request.FileHandler,
        #     urllib.request.HTTPErrorProcessor)
        tipoc = "I"
        for inv in self:
            if not inv.l10n_mx_edi_reason_cancellation:
                raise UserError('No se especifico un motivo de cancelacion')
            if inv.type == 'out_invoice':
                tipoc = "I"
            if inv.type == 'out_refund':
                tipoc = "E"

            uuids = inv.l10n_mx_edi_cfdi_uuid
            certificate_ids = inv.company_id.l10n_mx_edi_certificate_ids
            certificate_id = certificate_ids.sudo().get_valid_certificate()
            cer_pem = base64.encodestring(certificate_id.get_pem_cer(
                certificate_id.content)).decode('UTF-8')
            key_pem = base64.encodestring(certificate_id.get_pem_key(
                certificate_id.key, certificate_id.password)).decode('UTF-8')
            key_password = certificate_id.password

            if inv.l10n_mx_edi_reason_cancellation == '01':
                cadenacancela += '\nUUIDREL=' + inv.l10n_mx_edi_invoices_replace

            cer_ori = certificate_id.content.decode('UTF-8')
            # _logger.info(_('cer_ori: %s' % cer_ori))
            key_ori = certificate_id.key.decode('UTF-8')
            # _logger.info(_('key_ori: %s' % key_ori))

            data = cadenacancela.format(
                inv.company_id.partner_id.vat,
                username,
                password,
                uuids,
                # cer_pem.replace('\n', ''),
                cer_ori,
                inv.l10n_mx_edi_cfdi_customer_rfc,
                tipoc,
                "%.2f" % inv.amount_total,
                'sistemas@gebesa.com',
                'sistemas@gebesa.com',
                key_ori,
                # key_pem.replace('\n', ''),
                key_password,
                inv.l10n_mx_edi_reason_cancellation).encode()

            _logger.info(
                _('Cancel Data: %s' % data))
            try:
                req = urllib.request.Request(
                    url=url,
                    data=data,
                    headers={'Content-Type': 'text/plain'})
            except Exception as exc:
                err = str(exc) + 'uuids: ' + uuids + 'rfc cliente: ' +\
                    inv.l10n_mx_edi_cfdi_customer_rfc + 'rfc emisor: ' +\
                    inv.company_id.partner_id.vat + 'total: ' + "%.2f" % inv.amount_total +\
                    'tipoc: ' + tipoc
                inv.l10n_mx_edi_log_error(err)
                continue
            # response = http.open(req)
            # response_text = response.read()
            response = urllib.request.urlopen(req)
            response_text = response.read()
            _logger.info(
                _('response_text: %s' % response_text))
            try:
                if response_text == b'':
                    errmsge = response.headers['errmsg']
                    inv.l10n_mx_edi_log_error(errmsge + " data: " + data.decode())
                    continue

                xml = minidom.parseString(response_text)
            except Exception as exc:
                inv.l10n_mx_edi_log_error(str(exc))
                continue

            estatusuuid = xml.documentElement.getElementsByTagName(
                "EstatusUUID")[0].firstChild.nodeValue
            uuids = xml.documentElement.getElementsByTagName(
                "UUID")[0].firstChild.nodeValue

            code = str(estatusuuid)
            cancelled = code in ('201', '202')  # cancelled or previously cancelled
            if cancelled:
                data_attach = {
                    'name': 'acuse_cancelacion_' + uuids + '.xml',
                    'datas': base64.encodestring(
                        response_text and
                        response_text or ''),
                    'datas_fname': 'acuse_cancelacion_' + uuids + '.xml',
                    'description': _(
                        'XML Acuse de cancelacion de: %s.' % inv.number),
                    'res_model': 'account.invoice',
                    'res_id': inv.id,
                }
                self.env['ir.attachment'].with_context({}).create(data_attach)
            # no show code and response message if cancel was success
            msg = '' if cancelled else _(
                ' Cfdi No encontrado o no corresponde al emisor.\n- El uuid'
                ' es:') + uuids
            code = '' if cancelled else code
            inv._l10n_mx_edi_post_cancel_process(cancelled, code, msg)

    @api.multi
    def _l10n_mx_edi_post_sign_process(self, xml_signed, code=None, msg=None):
        '''Post process the results of the sign service.

        :param xml_signed: the xml signed datas codified in base64
        :param code: an eventual error code
        :param msg: an eventual error msg
        '''
        self.ensure_one()
        if xml_signed:
            # Post append addenda
            body_msg = _('The sign service has been called with success')
            # Update the pac status
            self.l10n_mx_edi_pac_status = 'signed'
            self.l10n_mx_edi_cfdi = xml_signed

            cfdi = base64.decodestring(xml_signed).replace(
                b'xmlns:schemaLocation', b'xsi:schemaLocation')
            tree = self.l10n_mx_edi_get_xml_etree(cfdi)
            # if already signed, extract uuid
            tfd_node = self.l10n_mx_edi_get_tfd_etree(tree)
            if tfd_node is not None:
                self.cfdi_uuid = tfd_node.get('UUID')

            # Update the content of the attachment
            attachment_id = self.l10n_mx_edi_retrieve_last_attachment()
            attachment_id.write({
                'datas': xml_signed,
                'mimetype': 'application/xml'
            })
            xml_signed = self.l10n_mx_edi_append_addenda(xml_signed)
            post_msg = [_('The content of the attachment has been updated')]
        else:
            body_msg = _('The sign service requested failed')
            post_msg = []
            extend = ' '
            if code:
                extend += 'Code: %s' % code
            if msg:
                extend += 'Message: %s' % msg
            raise UserError(_('The sign service requested failed') +
                            extend)
        if code:
            post_msg.extend([_('Code: %s') % code])
        if msg:
            post_msg.extend([_('Message: %s') % msg])
            # raise UserError(_(post_msg))
        self.message_post(
            body=body_msg + create_list_html(post_msg),
            subtype='account.mt_invoice_validated')

    @api.multi
    def _l10n_mx_edi_post_cancel_process(self, cancelled, code=None, msg=None):
        '''Post process the results of the cancel service.

        :param cancelled: is the cancel has been done with success
        :param code: an eventual error code
        :param msg: an eventual error msg
        '''

        self.ensure_one()
        if cancelled:
            body_msg = _('The cancel service has been called with success')
            self.l10n_mx_edi_pac_status = 'cancelled'
        else:
            body_msg = _('The cancel service requested failed')
            extend = ' '
            if code:
                extend += 'Code: %s' % code
            if msg:
                extend += 'Message: %s' % msg
            raise UserError(_('The cancel service requested failed') +
                            extend)
        post_msg = []
        if code:
            post_msg.extend([_('Code: %s') % code])
        if msg:
            post_msg.extend([_('Message: %s') % msg])
            # raise UserError(_(post_msg))
        self.message_post(
            body=body_msg + create_list_html(post_msg),
            subtype='account.mt_invoice_validated')

    @api.multi
    def l10n_mx_edi_check_cancel_status(self):
        '''CANCEL for Comercio digital.
        '''
        pac_name = self.env.user.company_id.l10n_mx_edi_pac
        if not pac_name:
            return {
                'error': _(
                    'Please check your configuration: ') + create_list_html([
                        'No PAC specified.'])}
        # Get the informations about the pac
        pac_info_func = '_l10n_mx_edi_%s_info' % pac_name
        pac_info = getattr(self, pac_info_func)(
            self.env.user.company_id, 'check')

        url = pac_info['url']
        username = pac_info['username']
        password = pac_info['password']
        cadenacancela1 = "RFCE={0}\nUSER={1}\nPWDW={2}\nUUID={3}\nCERT={4}"
        cadenacancela2 = "\nRFCR={5}\nTIPOC={6}\nTOTAL={7}\nEMAILE={8}\nEMAILR={9}"
        cadenacancela3 = "\nKEYF={10}\nPWDK={11}\nACUS=SI\nTIPO=cfdi3.3"
        cadenacancela = cadenacancela1 + cadenacancela2 + cadenacancela3
        # http = urllib.request.build_opener(
        #     urllib.request.ProxyHandler, urllib.request.UnknownHandler,
        #     urllib.request.HTTPHandler, urllib.request.HTTPDefaultErrorHandler,
        #     urllib.request.FTPHandler, urllib.request.FileHandler,
        #     urllib.request.HTTPErrorProcessor)
        tipoc = "I"
        for inv in self:
            if inv.type == 'out_invoice':
                tipoc = "I"
            if inv.type == 'out_refund':
                tipoc = "E"

            uuids = inv.l10n_mx_edi_cfdi_uuid
            certificate_ids = inv.company_id.l10n_mx_edi_certificate_ids
            certificate_id = certificate_ids.sudo().get_valid_certificate()
            cer_pem = base64.encodestring(certificate_id.get_pem_cer(
                certificate_id.content)).decode('UTF-8')
            key_pem = base64.encodestring(certificate_id.get_pem_key(
                certificate_id.key, certificate_id.password)).decode('UTF-8')
            key_password = certificate_id.password
            data = cadenacancela.format(
                inv.company_id.partner_id.vat,
                username,
                password,
                uuids,
                cer_pem.replace('\n', ''),
                inv.l10n_mx_edi_cfdi_customer_rfc,
                tipoc,
                "%.2f" % inv.amount_total,
                'sistemas@gebesa.com',
                'sistemas@gebesa.com',
                key_pem,
                key_password).encode()
            try:
                req = urllib.request.Request(
                    url=url,
                    data=data,
                    headers={'Content-Type': 'text/plain'})
            except Exception as exc:
                inv.l10n_mx_edi_log_error(str(exc))
                continue

            # response = http.open(req)
            # response_text = response.read()
            response = urllib.request.urlopen(req)
            response_text = response.read()

            inv.message_post(
                body=response_text,
                subtype='account.mt_invoice_validated')

    @api.multi
    def l10n_mx_edi_send_cfdi_email(self):
        now = fields.Date.today()
        invoices = self.search([
            ('type', 'in', ['out_invoice', 'out_refund']),
            ('cfdi_send', '!=', True),
            ('state', 'not in', ['draft', 'cancel'])], order="id")
        for inv in invoices:
            if (now - inv.date_invoice).days > 5:
                inv.cfdi_send = True
                continue
            if inv.l10n_mx_edi_is_required():
                if not inv.l10n_mx_edi_cfdi_uuid:
                    continue
            inv.send_email_invoice()

        payment_obj = self.env['account.payment']
        payments = payment_obj.search([
            ('payment_type', 'in', ['inbound']),
            ('cfdi_send', '!=', True),
            ('state', 'not in', ['draft', 'cancelled'])
        ], order="id")
        for pay in payments.filtered(lambda r: r.l10n_mx_edi_is_required()):
            if (now - pay.payment_date).days > 5:
                pay.cfdi_send = True
                continue
            if pay.l10n_mx_edi_cfdi_uuid:
                pay.send_email_payment()

    @api.multi
    def l10n_mx_edi_log_error(self, message):
        self.ensure_one()
        raise UserError(_(
            'Error during the process: %s') % message)


class AccountInvoiceLine(models.Model):
    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'

    l10n_mx_edi_tax_object = fields.Selection([
        ('01', 'No objeto de impuesto'),
        ('02', 'Sí objeto de impuesto'),
        ('03', 'Sí objeto del impuesto y no obligado al desglose'),
    ], string='Objeto de impuesto',
        compute='_compute_l10n_mx_edi_tax_object',
        store=True,
    )

    @api.depends('invoice_line_tax_ids')
    def _compute_l10n_mx_edi_tax_object(self):
        for line in self:
            if line.invoice_line_tax_ids:
                line.l10n_mx_edi_tax_object = '02'
            else:
                line.l10n_mx_edi_tax_object = '01'
