# Copyright 2020, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


import base64
import urllib.request
import logging
from xml.dom import minidom
from codecs import BOM_UTF8
from datetime import datetime
import requests

from odoo import _, api, fields, models, tools
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from odoo.exceptions import UserError
# from odoo.tools import float_round
# from io import BytesIO
# from odoo.tools.xml_utils import _check_with_xsd
from lxml import etree
from . import account_invoice

BOM_UTF8U = BOM_UTF8.decode('UTF-8')
CFDI_TEMPLATE = 'l10n_mx_edi.payment10'
CFDI_XSLT_CADENA = 'l10n_mx_edi/data/3.3/cadenaoriginal.xslt'
CFDI_XSLT_CADENA_TFD = 'l10n_mx_edi/data/xslt/3.3/cadenaoriginal_TFD_1_1.xslt'

CFDI_TEMPLATE20 = 'l10n_mx_edi_extended.payment20'
CFDI_XSLT_CADENA20 = 'l10n_mx_edi_extended/data/4.0/cadenaoriginal.xslt'

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    cfdi_send = fields.Boolean(
        string='CFDI send',
    )
    rate_mex = fields.Float(
        string='Tipo de cambio',
        help='Paridad utilizada en la fecha de la factura',
        compute='_compute_rate_mex',
    )
    l10n_mx_edi_reason_cancellation = fields.Selection(
        [('01', 'Comprobante emitido con errores con relacion'),
         ('02', 'Comprobante emitido con errores sin relacion'),
         ('03', 'No se llevo a cabo la operación'),
         ('04', 'Operación nominativa relacionada en la factura global')],
        string='Motivo de cancelacion',
    )
    l10n_mx_edi_invoices_replace = fields.Char(
        string='UUID que remplazan',
    )
    xml_intermediate = fields.Text(
        string='XML Intermediate',
        help='XML Intermediate',
    )

    @api.multi
    def action_read_intermediate_file(self):
        self.ensure_one()
        attachment_id = self.l10n_mx_edi_retrieve_last_attachment()
        if not attachment_id:
            return
        attachment_id = attachment_id[0]
        # At this moment, the attachment contains the file size in its 'datas' field because
        # to save some memory, the attachment will store its data on the physical disk.
        # To avoid this problem, we read the 'datas' directly on the disk.
        datas = attachment_id._file_read(attachment_id.store_fname)
        if not datas:
            _logger.exception('The CFDI attachment cannot be found')
            return
        self.xml_intermediate = base64.b64decode(datas).decode('UTF-8')

    def redo_stamp_chain_intermediate(self):
        cfdi = self.xml_intermediate.encode()
        version = self.l10n_mx_edi_get_pac_version()
        tree = self.l10n_mx_edi_get_xml_etree(cfdi)
        tree.attrib['Sello'] = ""
        if version == '1.0':
            cadena = self.env['account.invoice'].l10n_mx_edi_generate_cadena(
                CFDI_XSLT_CADENA, tree)
        elif version == '2.0':
            cadena = self.env['account.invoice'].l10n_mx_edi_generate_cadena(
                CFDI_XSLT_CADENA20, tree)

        certificate_id = self.company_id.l10n_mx_edi_certificate_ids.filtered(
            lambda cer: cer.serial_number == tree.attrib['NoCertificado'])

        tree.attrib['Sello'] = certificate_id.sudo(
        ).get_encrypted_cadena(cadena)
        res = b'<?xml version="1.0" encoding="UTF-8"?>' + etree.tostring(tree)

        return res

    @api.model
    def l10n_mx_edi_get_payment_etree(self, cfdi):
        '''Get the Complement node from the cfdi.

        :param cfdi: The cfdi as etree
        :return: the Payment node
        '''
        if not hasattr(cfdi, 'Complemento'):
            return None
        attribute = '//pago20:DoctoRelacionado'
        namespace = {'pago20': 'http://www.sat.gob.mx/Pagos20'}
        node = cfdi.Complemento.xpath(attribute, namespaces=namespace)
        return node

    @api.model
    def l10n_mx_edi_get_pac_version(self):
        '''Returns the cfdi version to generate the CFDI.
        '''
        version = self.env['ir.config_parameter'].sudo().get_param(
            'l10n_mx_edi_cfdi_payment_version', '1.0')
        return version

    @api.multi
    def cancel_payment_sat(self):
        for record in self.filtered(lambda r: r.l10n_mx_edi_is_required()):
            if not record.l10n_mx_edi_cfdi_uuid:
                raise UserError(_(
                    'The fiscal folio is needed to cancel the payment.'))
            record._l10n_mx_edi_cancel()

    @api.multi
    @api.depends('currency_id', 'payment_date')
    def _compute_rate_mex(self):
        for pay in self:
            date = pay.payment_date or fields.Date.today()
            query = """
                SELECT r.rate_mex FROM res_currency_rate r
                WHERE r.currency_id = %s AND r.name <= %s
                    AND (r.company_id IS NULL OR r.company_id = %s)
                ORDER BY r.company_id, r.name DESC LIMIT 1"""
            self._cr.execute(query, (pay.currency_id.id, date, self.env.user.company_id.id))
            currency_rates = self._cr.fetchall()
            if currency_rates:
                pay.rate_mex = currency_rates[0][0]
            else:
                pay.rate_mex = 1

    @api.multi
    def l10n_mx_edi_payment_data(self):
        # result = super(AccountPayment, self).l10n_mx_edi_payment_data()
        self.ensure_one()
        # Based on "En caso de no contar con la hora se debe registrar 12:00:00"
        mxn = self.env.ref('base.MXN')
        date = datetime.combine(
            fields.Datetime.from_string(self.payment_date),
            datetime.strptime('12:00:00', '%H:%M:%S').time()).strftime('%Y-%m-%dT%H:%M:%S')
        res = self._l10n_mx_edi_invoice_payment_data()
        total_paid = res.get('total_paid', 0)
        # total_curr = res.get('total_curr', 0)
        total_currency = res.get('total_currency', 0)
        # precision = self.env['decimal.precision'].precision_get('Account')

        ctx = dict(company_id=self.company_id.id, date=self.payment_date)
        rate = ('%.6f' % (self.currency_id.with_context(**ctx)._convert(
            1, mxn, self.company_id, self.payment_date, round=False))) if self.currency_id.name != 'MXN' else '1'

        company_bank = self.journal_id.bank_account_id
        payment_code = self.l10n_mx_edi_payment_method_id.code
        acc_receiver_ok = payment_code in [
            '02', '03', '04', '05', '28', '29', '99']
        pay_account_receiver = company_bank.acc_number[-10:] if len(
            company_bank.acc_number) > 10 else company_bank.acc_number.zfill(10)

        return {
            'mxn': mxn,
            'payment_date': date,
            'payment_rate': rate,
            'pay_vat_ord': False,
            'pay_account_ord': False,
            'pay_vat_receiver': False,
            'pay_ent_type': False,
            'pay_certificate': False,
            'pay_string': False,
            'pay_stamp': False,
            'total_paid': total_paid,
            'total_currency': total_currency,
            'pay_account_receiver': (pay_account_receiver or '').replace(
                ' ', '') if acc_receiver_ok else None,
        }

    @api.multi
    def l10n_mx_edi_is_required(self):
        self.ensure_one()
        required = (self.payment_type == 'inbound' and self.company_id.country_id == self.env.ref('base.mx') and not self.invoice_ids.filtered(lambda i: i.type != 'out_invoice'))
        if not required:
            self.cfdi_send = True
            return required
        if self.l10n_mx_edi_pac_status != 'none':
            return True
        if self.invoice_ids and (
                False in self.invoice_ids.mapped('l10n_mx_edi_cfdi_uuid') and False in self.invoice_ids.mapped('cfdi_uuid')):
            raise UserError(_(
                'Some of the invoices that will be paid with this record '
                'are not signed, and the UUID is required to indicate '
                'the invoices that are paid with this CFDI'))
        messages = []
        if not self.invoice_ids:
            messages.append(_(
                '<b>This payment <b>has not</b> invoices related.'
                '</b><br/><br/>'
                'Which actions can you take?\n'
                '<ul>'
                '<ol>If this is an payment advance, you need to create a new '
                'invoice with a product that will represent the payment in '
                'advance and reconcile such invoice with this payment. For '
                'more information please read '
                '<a href="http://omawww.sat.gob.mx/informacion_fiscal/factura_electronica/Documents/Complementoscfdi/Caso_uso_Anticipo.pdf">'
                'this SAT reference.</a></ol>'
                '<ol>If you already have the invoices that are paid make the '
                'payment matching of them.</ol>'
                '</ul>'
                '<p>If you follow this steps once you finish them and the '
                'paid amount is bellow the sum of invoices the payment '
                'will be automatically signed'
                '</p>'))
        categ_force = self._l10n_mx_edi_get_force_rep_category()
        force = self._context.get('force_ref') or (
            categ_force and categ_force in self.partner_id.category_id)
        if self.invoice_ids and not self.invoice_ids.filtered(
                lambda i: i.l10n_mx_edi_get_payment_method_cfdi() == 'PPD') and not force:
            messages.append(_(
                '<b>The invoices related with this payment have the payment '
                'method as <b>PUE</b>.'
                '</b><br/><br/>'
                'When an invoice has the payment method <b>PUE</b> do not '
                'requires generate a payment complement. For more information '
                'please read '
                '<a href="http://omawww.sat.gob.mx/informacion_fiscal/factura_electronica/Documents/Complementoscfdi/Guia_comple_pagos.pdf">'
                'this SAT reference.</a>, Pag. 3. Or read the '
                '<a href="https://www.odoo.com/documentation/user/11.0/es/accounting/localizations/mexico.html#payments-just-available-for-cfdi-3-3">'
                'Odoo documentation</a> to know how to indicate the payment '
                'method in the invoice CFDI.'))
        if messages:
            self.message_post(body=account_invoice.create_list_html(messages))
            self.cfdi_send = True
            return force or False
        return required

    @api.multi
    def _perform_l10n_mx_validations(self):

        for payment in self.filtered(lambda r: r.l10n_mx_edi_is_required()):
            # if not payment.company_id.partner_id.l10n_mx_edi_name:
            #     raise UserError(_(
            #         'The Company\'s partner have not a name for the cfdi.'))

            if not payment.company_id.partner_id.city_id:
                raise UserError(_(
                    'The Company\'s partner have not a City defined.'))

            if not payment.company_id.partner_id.state_id:
                raise UserError(_(
                    'The Company\'s partner have not a State defined.'))

            if not payment.company_id.partner_id.country_id:
                raise UserError(_(
                    'The Company\'s partner have not a Country defined.'))

            if not payment.company_id.partner_id.zip:
                raise UserError(_(
                    'The Company\'s partner have not a ZIP defined.'))

            if not payment.company_id.partner_id.property_account_position_id:
                raise UserError(_(
                    'The Company\'s partner have not an Account Position defined.'))

            if not payment.company_id.partner_id.property_account_position_id.l10n_mx_edi_code:
                raise UserError(_(
                    'The Company\'s partner Account position have not a Code defined.'))

            # if not payment.partner_id.l10n_mx_edi_name:
            #     raise UserError(_(
            #         'Partner have not name for cfdi. Please set that value.'))

    @api.multi
    def post(self):
        """Generate CFDI to payment after that invoice is paid"""
        self._perform_l10n_mx_validations()

        # --------------------------------------------------
        # Ajustar la suma de las facturas al total del pago
        # --------------------------------------------------
        for payment in self:
            totcalc = 0.0
            for line in payment.register_line_ids:
                totcalc += line.amount

            if abs(payment.amount - totcalc) < 0.08:
                payment.write({'amount': totcalc})

            _logger.error(
                _('ctto- valor del pago %s' % payment.amount))

            _logger.error(
                _('ctto- suma de las lineas %s' % totcalc))

        res = super(AccountPayment, self.with_context(
            l10n_mx_edi_manual_reconciliation=False)).post()
        # for record in self.filtered(lambda r: r.l10n_mx_edi_is_required()):
        #     pdf = record.attachment_payment_pdf()
        #     record.send_email_payment(pdf=pdf)
        return res

    def attachment_payment_pdf(self):
        """ Sign the xml file
        """
        attachment = self.env['ir.attachment']

        report = self.env['ir.actions.report']._get_report_from_name(
            'l10n_mx_base.l10n_mx_base_report_payment')
        pdf = report.render_qweb_pdf(self.id)[0]
        namepdf = ('%s-%s-MX-Payment-10.pdf' % (
            self.journal_id.code, self.name))
        data_attach = {
            'name': namepdf,
            'datas': base64.encodestring(pdf or ''),
            'datas_fname': self.company_id.vat + '_' + self.name + '.pdf',
            'res_model': 'account.payment',
            'res_id': self.id,
        }
        return attachment.create(data_attach)

    def send_email_payment(self):
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
            # message = record.action_invoice_sent()
            tmp = self.env.ref('l10n_mx_base.email_template_edi_payment', False)

            # attachmnts = [self.l10n_mx_edi_retrieve_attachments().id]
            # attachmnts.append(pdf.id)
            pdf = record.attachment_payment_pdf()
            attachmnts = [(6, 0, [pdf.id])]

            mail = self.env['mail.compose.message'].with_context(
                dict(
                    default_model='account.payment',
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
                    tmp.id, None, 'account.payment', record.id).get(
                        'value', {})
            except BaseException as exc:
                _logger.info("payment not sent even if configured. %s")
                data.update({'subject': str(exc)})
                errored = True

            # partners = []
            # if data.get('partner_ids'):
            #     partners = data.get('partner_ids', [])
            # else:
            #     partners = [(6, 0, [record.partner_id.id])]

            mail.write({
                'body': data.get('body', 'payment not sent because an '
                                         'error rendering or generating '
                                         'the email'),
                # 'partner_ids': partners,
                'email_from': data.get('email_from', 'noreply@gebesa.com'),
                'attachment_ids': attachmnts,
                # 'attachment_ids': data.get('attachment_ids', []),
                'subject': ('%s Payment receipt' % (record.company_id.name)),
            })
            mail.with_context(mark_invoice_as_sent=True).send_mail()
            mail = self.env['mail.mail'].search([
                ('res_id', '=', record.id),
                ('model', '=', 'account.payment'),
                ('subject', '=', ('%s Payment receipt' % (record.company_id.name)))], limit=1)
            if not mail and not errored:
                # record.cfdi_send = True
                query = """
                    UPDATE account_payment SET cfdi_send = True
                    WHERE id = %s
                """ % record.id
                self.env.cr.execute(query)
                continue
            # record.write({'sent': False})
            record.message_post(
                subject='Error when try send invoice by email',

                body='<br>'.join(["- " + msg.failure_reason for msg in mail
                                  if msg.failure_reason]))

    @api.multi
    def _l10n_mx_edi_create_cfdi_payment(self):
        self.ensure_one()
        qweb = self.env['ir.qweb']
        error_log = []
        company_id = self.company_id
        pac_name = company_id.l10n_mx_edi_pac

        version = self.l10n_mx_edi_get_pac_version()

        if not self.company_id.partner_id.commercial_partner_id.l10n_mx_edi_name:
            self.company_id.partner_id.commercial_partner_id._l10n_mx_edi_clean_to_legal_name()
        if not self.partner_id.commercial_partner_id.l10n_mx_edi_name:
            self.partner_id.commercial_partner_id._l10n_mx_edi_clean_to_legal_name()

        values = self._l10n_mx_edi_create_cfdi_values()

        values['tax_name'] = lambda t: {'ISR': '001', 'IVA': '002', 'IEPS': '003'}.get(
            t, False)
        if 'error' in values:
            error_log.append(values.get('error'))

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
            return {'error': _('Please check your configuration: ') + account_invoice.create_list_html(error_log)}

        # -Compute date and time of the invoice
        partner = self.journal_id.l10n_mx_address_issued_id or self.company_id.partner_id.commercial_partner_id
        tz = self.env['account.invoice']._l10n_mx_edi_get_timezone(
            partner.state_id.code)
        date_mx = datetime.now(tz)
        time_invoice = date_mx.strftime(DEFAULT_SERVER_TIME_FORMAT)

        # -----------------------
        # Create the EDI document
        # -----------------------

        # -Compute certificate data
        today = fields.Date.context_today(self)
        values['date'] = datetime.combine(
            fields.Datetime.from_string(today),
            datetime.strptime(time_invoice, '%H:%M:%S').time()).strftime('%Y-%m-%dT%H:%M:%S')
        values['certificate_number'] = certificate_id.serial_number
        values['certificate'] = certificate_id.sudo().get_data()[0]

        payment_date = datetime.combine(
            fields.Datetime.from_string(self.payment_date),
            datetime.strptime(time_invoice, '%H:%M:%S').time()).strftime('%Y-%m-%dT%H:%M:%S')

        values.update({'payment_date': payment_date, })

        customer = values['customer']
        if self.partner_id.commercial_partner_id.l10n_mx_edi_get_customer_rfc() == 'XEXX010101000':
            values.update({
                'receiver_reg_trib': customer.vat})
        # -Compute cfdi
        if version == '1.0':
            cfdi = qweb.render(CFDI_TEMPLATE, values=values)
            cfdi = cfdi.replace(
                b'\n            <cfdi:Comprobante',
                b'<?xml version="1.0" encoding="UTF-8"?><cfdi:Comprobante')
            tree = self.l10n_mx_edi_get_xml_etree(cfdi)
            cadena = self.env['account.invoice'].l10n_mx_edi_generate_cadena(
                CFDI_XSLT_CADENA, tree)
        elif version == '2.0':
            cfdi = qweb.render(CFDI_TEMPLATE20, values=values)
            cfdi = cfdi.replace(
                b'\n            <cfdi:Comprobante',
                b'<?xml version="1.0" encoding="UTF-8"?><cfdi:Comprobante')
            tree = self.l10n_mx_edi_get_xml_etree(cfdi)
            cadena = self.env['account.invoice'].l10n_mx_edi_generate_cadena(
                CFDI_XSLT_CADENA20, tree)
        else:
            raise UserError(_('Unsupported version %s') % version)
            return {'error': _('Unsupported version %s') % version}

        # Post append cadena
        tree.attrib['Sello'] = certificate_id.sudo().get_encrypted_cadena(cadena)

        # TODO - Check with XSD
        # return {'cfdi': etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')}
        res = {'cfdi': b'<?xml version="1.0" encoding="UTF-8"?>' + etree.tostring(tree)}
        return res
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
            if version == '1.0':
                url = 'https://pruebas.comercio-digital.mx/timbre/timbrarV5.aspx'\
                    if test else 'https://ws.comercio-digital.mx/timbre/timbrarV5.aspx'
            else:
                url = 'https://pruebas.comercio-digital.mx/timbre4/timbrarV5'\
                    if test else 'https://ws.comercio-digital.mx/timbre4/timbrarV5'
        elif service_type == 'cancel':
            url = 'https://pruebas.comercio-digital.mx/cancela4/cancelarUuid'\
                if test else 'https://cancela.comercio-digital.mx/cancela4/cancelarUuid'
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

        for payment in self:
            if payment.xml_intermediate:
                cfdi = payment.redo_stamp_chain_intermediate()
            else:
                cfdi = base64.b64decode(payment.l10n_mx_edi_cfdi).decode('UTF-8')
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
                payment.l10n_mx_edi_log_error(str(exc))
                continue
            # res = _(tools.ustr(response.text))
            code = _(tools.ustr(response.headers['codigo']))
            msg = ''
            if code and\
               code != '000':
                msg = _(tools.ustr(response.headers['errmsg']))

            xml_signed = response.content.decode('UTF-8')

            if xml_signed:
                xml_signed = base64.b64encode(xml_signed.encode('utf-8'))

            payment._l10n_mx_edi_post_sign_process(
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
        tipoc = "P"
        for payment in self:
            if not payment.l10n_mx_edi_reason_cancellation:
                payment.l10n_mx_edi_log_error('No se especifico un motivo de cancelacion')
                continue
                # raise UserError('No se especifico un motivo de cancelacion')
            uuids = payment.l10n_mx_edi_cfdi_uuid
            certificate_ids = payment.company_id.l10n_mx_edi_certificate_ids
            certificate_id = certificate_ids.sudo().get_valid_certificate()
            # cer_pem = base64.encodestring(certificate_id.get_pem_cer(
            #     certificate_id.content)).decode('UTF-8')
            cer_ori = certificate_id.content.decode('UTF-8')
            # key_pem = base64.encodestring(certificate_id.get_pem_key(
            #     certificate_id.key, certificate_id.password)).decode('UTF-8')
            key_ori = certificate_id.key.decode('UTF-8')
            key_password = certificate_id.password

            if payment.l10n_mx_edi_reason_cancellation == '01':
                cadenacancela += '\nUUIDREL=' + payment.l10n_mx_edi_invoices_replace

            data = cadenacancela.format(
                payment.company_id.partner_id.vat,
                username,
                password,
                uuids,
                cer_ori,
                # cer_pem.replace('\n', ''),
                payment.l10n_mx_edi_cfdi_customer_rfc,
                tipoc,
                "%.2f" % payment.amount,
                'sistemas@gebesa.com',
                'sistemas@gebesa.com',
                key_ori,
                # key_pem.replace('\n', ''),
                key_password,
                payment.l10n_mx_edi_reason_cancellation).encode()
            print(data)
            try:
                req = urllib.request.Request(
                    url=url,
                    data=data,
                    headers={'Content-Type': 'text/plain'})
            except Exception as exc:
                err = str(exc) + 'uuids: ' + uuids + 'rfc cliente: ' +\
                    payment.l10n_mx_edi_cfdi_customer_rfc + 'rfc emisor: ' +\
                    payment.company_id.partner_id.vat + 'total: ' + "%.2f" % payment.amount_total +\
                    'tipoc: ' + tipoc
                payment.l10n_mx_edi_log_error(err)
                continue

            # response = http.open(req)
            # response_text = response.read()
            response = urllib.request.urlopen(req)
            response_text = response.read()
            print(response_text)
            try:
                if response_text == b'':
                    errmsge = response.headers['errmsg']
                    payment.l10n_mx_edi_log_error(errmsge + " data: " + data.decode())
                    continue
                xml = minidom.parseString(response_text)
            except Exception as exc:
                payment.l10n_mx_edi_log_error(str(exc))
                continue

            estatusuuid = xml.documentElement.getElementsByTagName("EstatusUUID")[0].firstChild.nodeValue
            uuids = xml.documentElement.getElementsByTagName("UUID")[0].firstChild.nodeValue

            code = str(estatusuuid)
            cancelled = code in ('201', '202')  # cancelled or previously cancelled
            if cancelled:
                data_attach = {
                    'name': 'acuse_cancelacion_' + uuids + '.xml',
                    'datas': base64.encodestring(
                        response_text and response_text or ''),
                    'datas_fname': 'acuse_cancelacion_' + uuids + '.xml',
                    'description': _(
                        'XML Acuse de cancelacion de: %s.' % payment.name),
                    'res_model': 'account.payment',
                    'res_id': payment.id,
                }
                self.env['ir.attachment'].with_context({}).create(data_attach)
            # no show code and response message if cancel was success
            msg = '' if cancelled else _(
                ' Cfdi No encontrado o no corresponde al emisor.\n- El uuid'
                ' es:') + uuids
            code = '' if cancelled else code
            payment._l10n_mx_edi_post_cancel_process(cancelled, code, msg)

    @api.multi
    def _l10n_mx_edi_retry(self):
        rep_is_required = self.filtered(lambda r: r.l10n_mx_edi_is_required())
        version = self.l10n_mx_edi_get_pac_version().replace('.', '')
        for rec in rep_is_required:
            cfdi_values = rec._l10n_mx_edi_create_cfdi_payment()
            error = cfdi_values.pop('error', None)
            cfdi = cfdi_values.pop('cfdi', None)
            if error:
                # cfdi failed to be generated
                rec.l10n_mx_edi_pac_status = 'retry'
                rec.message_post(body=error)
                continue
            # cfdi has been successfully generated
            rec.l10n_mx_edi_pac_status = 'to_sign'
            filename = ('%s-%s-MX-Payment-%s.xml' % (
                rec.journal_id.code, rec.name, version))
            ctx = self.env.context.copy()
            ctx.pop('default_type', False)
            rec.l10n_mx_edi_cfdi_name = filename
            attachment_id = self.env['ir.attachment'].with_context(ctx).create({
                'name': filename,
                'res_id': rec.id,
                'res_model': rec._name,
                'datas': base64.encodestring(cfdi),
                'datas_fname': filename,
                'description': _('Mexican CFDI to payment'),
            })
            rec.message_post(
                body=_('CFDI document generated (may be not signed)'),
                attachment_ids=[attachment_id.id])
            rec._l10n_mx_edi_sign()
        (self - rep_is_required).write({
            'l10n_mx_edi_pac_status': 'none',
        })

    @api.multi
    def _l10n_mx_edi_create_taxes_cfdi_values(self, payment_rate):
        '''Create the taxes values to fill the CFDI template.
        '''
        self.ensure_one()
        values = {
            'TotalRetencionesIVA': 0,
            'TotalRetencionesISR': 0,
            'TotalRetencionesIEPS': 0,
            'TotalTrasladosBaseIVA16': 0,
            'TotalTrasladosImpuestoIVA16': 0,
            'TotalTrasladosBaseIVA8': 0,
            'TotalTrasladosImpuestoIVA8': 0,
            'TotalTrasladosBaseIVA0': 0,
            'TotalTrasladosImpuestoIVA0': 0,
            'TotalTrasladosBaseIVAExento': 0,
            'MontoTotalPagos': 0,
            'RetencionesP': {},
            'TrasladosP': {},
            'invoices': {}
        }

        invoice_base = {
            'IVA16': [],
            'IVA8': [],
            'IVA0': [],
        }
        payment_rate = float(payment_rate)
        for invoice in self.invoice_ids:
            values['invoices'][invoice.id] = {
                'retenciones': [],
                'traslados': []
            }
            taxes = invoice._l10n_mx_edi_create_taxes_cfdi_values()
            pago = [pag for pag in invoice._get_payments_vals() if (
                pag.get('account_payment_id', False) == self.id or not pag.get(
                    'account_payment_id') and (not pag.get(
                        'invoice_id') or pag.get('invoice_id') == invoice.id))]

            payment_amount = pago[0]['amount'] or 0.0
            payment_perc = round(payment_amount / invoice.amount_total, 6)
            # base_amount = round(invoice.amount_untaxed * payment_perc, 2)

            values['MontoTotalPagos'] += round(payment_amount * payment_rate, 2)

            for withhold in taxes['withholding']:
                base_amount = round(withhold['base'] * payment_perc, 2)

                tax_amount = round(base_amount * withhold['rate'], 4)

                if withhold['name'] == 'IVA':
                    values['TotalRetencionesIVA'] += tax_amount * payment_rate
                if withhold['name'] == 'ISR':
                    values['TotalRetencionesISR'] += tax_amount * payment_rate
                if withhold['name'] == 'IEPS':
                    values['TotalRetencionesIEPS'] += tax_amount * payment_rate

                key = withhold['name'] + '|' + str(withhold['rate']) + '|' + withhold['type']

                if key in values['RetencionesP']:
                    values['RetencionesP'][key]['amount'] += tax_amount
                else:
                    values['RetencionesP'][key] = {
                        'name': withhold['name'],
                        'rate': withhold['rate'],
                        'type': withhold['type'],
                        'amount': tax_amount
                    }

                values['invoices'][invoice.id]['retenciones'].append((
                    base_amount, withhold['name'], withhold['type'],
                    withhold['rate'], round(base_amount * withhold['rate'], 4)))

            for transferred in taxes['transferred']:
                base_amount = round(transferred['base'] * payment_perc, 2)

                tax_amount = round(base_amount * transferred['rate'], 4)

                if transferred['name'] == 'IVA':
                    if transferred['rate'] == 0.16:
                        values['TotalTrasladosImpuestoIVA16'] += (
                            tax_amount * payment_rate)
                        if invoice.id not in invoice_base['IVA16']:
                            values['TotalTrasladosBaseIVA16'] += base_amount * payment_rate
                            invoice_base['IVA16'].append(invoice.id)

                    if transferred['rate'] == 0.08:
                        values['TotalTrasladosImpuestoIVA8'] += (
                            tax_amount * payment_rate)
                        if invoice.id not in invoice_base['IVA8']:
                            values['TotalTrasladosBaseIVA8'] += base_amount * payment_rate
                            invoice_base['IVA8'].append(invoice.id)

                    if transferred['rate'] == 0.00:
                        base_amount = payment_amount
                        values['TotalTrasladosImpuestoIVA0'] += (
                            tax_amount * payment_rate)
                        if invoice.id not in invoice_base['IVA0']:
                            values['TotalTrasladosBaseIVA0'] += round(base_amount * payment_rate, 2)
                            invoice_base['IVA0'].append(invoice.id)

                key = transferred['name'] + '|' + str(transferred['rate']) + '|' + transferred['type']

                if key in values['TrasladosP']:
                    values['TrasladosP'][key]['amount'] += tax_amount
                    if invoice.id not in values['TrasladosP'][key]['invoices']:
                        values['TrasladosP'][key]['base'] += base_amount
                        values['TrasladosP'][key]['invoices'].append(invoice.id)

                else:
                    values['TrasladosP'][key] = {
                        'name': transferred['name'],
                        'rate': transferred['rate'],
                        'type': transferred['type'],
                        'amount': tax_amount,
                        'base': base_amount,
                        'invoices': [invoice.id]
                    }

                values['invoices'][invoice.id]['traslados'].append((
                    base_amount, transferred['name'], transferred['type'],
                    transferred['rate'], round(
                        base_amount * transferred['rate'], 4)))

        return values
