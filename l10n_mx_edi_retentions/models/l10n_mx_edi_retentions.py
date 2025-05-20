# -*- coding: utf-8 -*-

from xml.dom import minidom
import base64
import logging
from itertools import groupby
import urllib.request
from lxml.objectify import fromstring
from lxml import etree
import requests

from odoo import _, api, exceptions, fields, models, tools
_logger = logging.getLogger(__name__)

CFDI_TEMPLATE_10 = 'l10n_mx_edi_retentions.retention_cfdiv10'
CFDI_XSLT_CADENA = 'l10n_mx_edi_retentions/data/xslt/%s/retenciones.xslt'
CFDI_XSLT_CADENA_TFD = 'l10n_mx_edi_retentions/data/xslt/1.0/retenciones.xslt'

MONTH_SELECTION = [
    (1, 'January'), (2, 'February'),
    (3, 'March'), (4, 'April'),
    (5, 'May'), (6, 'June'),
    (7, 'July'), (8, 'August'),
    (9, 'September'), (10, 'October'),
    (11, 'November'), (12, 'December')]


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


class L10nMxEdiRetentions(models.Model):
    _name = 'l10n_mx_edi.retentions'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Retentions"
    _order = 'number desc'
    _rec_name = 'number'

    number = fields.Char(
        string='Number',
        size=250,
        required=True,
        index=True,
        copy=False,
        default='New',
        track_visibility='always'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'retentions.retentions'),
        track_visibility='always'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id')
    initial_month = fields.Selection(
        MONTH_SELECTION,
        string='Initial month',
    )
    final_month = fields.Selection(
        MONTH_SELECTION,
        string='Final month',
    )
    fiscal_year = fields.Selection([
        (2020, '2020'), (2021, '2021'),
        (2022, '2022'), (2023, '2023'),
        (2024, '2024'), (2025, '2025'),
        (2026, '2026'), (2027, '2027'),
        (2028, '2028'), (2029, '2029'),
        (2030, '2030'), ],
        string='Fiscal year',
    )
    date = fields.Datetime(
        string='Date',
        default=fields.Datetime.now,
        readonly=True
    )
    retention_type_id = fields.Many2one(
        'l10n_mx_edi.retentions.type',
        string='Retention type',
    )
    retention_type_code = fields.Char(
        related='retention_type_id.code',
        string='Code',
    )
    operation_amount = fields.Float(
        string="Operation amount",
        required=True
    )
    taxed_amount = fields.Float(
        string="Taxed amount",
        required=True
    )
    exempt_amount = fields.Float(
        string="Exempt amount",
        required=True
    )
    required_amount = fields.Float(
        string="Required amount",
        compute='_compute_required_amount',
        store=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        string="Receiver"
    )
    retentions_detail_ids = fields.One2many(
        'l10n_mx_edi.retentions.taxes',
        'retentions_id',
        string="Retentions Line"
    )
    retentions_complement_ids = fields.One2many(
        'l10n_mx_edi.retentions.complement',
        'retentions_id',
        string="Retentions Complement"
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('valid', 'Valid'),
         ('cancel', 'Cancelled')],
        string='Status',
        index=True,
        readonly=True,
        default='draft',
        track_visibility='onchange',
        copy=False,
        help="State of the retention"
    )
    l10n_mx_edi_cfdi = fields.Binary(
        string='Cfdi content', copy=False, readonly=True,
        help='The cfdi xml content encoded in base64.',
        compute='_compute_cfdi_values'
    )
    l10n_mx_edi_cfdi_uuid = fields.Char(
        string='Fiscal Folio',
        copy=False,
        readonly=True,
        help='Folio in electronic retention, is returned by SAT when send to stamp.',
        compute='_compute_cfdi_values'
    )
    l10n_mx_edi_cfdi_issuing_rfc = fields.Char(
        'Issuing RFC',
        copy=False,
        readonly=True,
        help='The supplier tax identification number.',
        compute='_compute_cfdi_values'
    )
    l10n_mx_edi_cfdi_receptor_rfc = fields.Char(
        'Receptor RFC',
        copy=False,
        readonly=True,
        help='The customer tax identification number.',
        compute='_compute_cfdi_values'
    )
    l10n_mx_edi_pac_status = fields.Selection(
        selection=[
            ('retry', 'Retry'),
            ('to_sign', 'To sign'),
            ('signed', 'Signed'),
            ('to_cancel', 'To cancel'),
            ('cancelled', 'Cancelled')
        ],
        string='PAC status',
        help='Refers to the status of the retention inside the PAC.',
        readonly=True,
        copy=False
    )
    l10n_mx_edi_sat_status = fields.Selection(
        selection=[
            ('none', 'State not defined'),
            ('undefined', 'Not Synced Yet'),
            ('not_found', 'Not Found'),
            ('cancelled', 'Cancelled'),
            ('valid', 'Valid'),
        ],
        string='SAT status',
        help='Refers to the status of the retention inside the SAT system.',
        readonly=True,
        copy=False,
        required=True,
        track_visibility='onchange',
        default='undefined'
    )
    l10n_mx_edi_cfdi_certificate_id = fields.Many2one(
        'l10n_mx_edi.certificate',
        string='Certificate',
        copy=False,
        readonly=True,
        help='The certificate used during the generation of the cfdi.',
        compute='_compute_cfdi_values'
    )
    l10n_mx_edi_cfdi_name = fields.Char(
        string='CFDI name',
        copy=False,
        readonly=True,
        help='The attachment name of the CFDI.'
    )

    _sql_constraints = [
        ('number_uniq', 'unique (number, company_id)',
         'Retention Number must be unique per Company!')
    ]

    @api.multi
    @api.depends('l10n_mx_edi_cfdi_name')
    def _compute_cfdi_values(self):
        '''Fill the retention fields from the cfdi values.
        '''
        for ret in self:
            attachment_id = ret.l10n_mx_edi_retrieve_last_attachment()
            if not attachment_id:
                continue
            # At this moment, the attachment contains the file size in its 'datas' field because
            # to save some memory, the attachment will store its data on the physical disk.
            # To avoid this problem, we read the 'datas' directly on the disk.
            datas = attachment_id._file_read(attachment_id.store_fname)
            if not datas:
                _logger.exception('The CFDI attachment cannot be found')
                continue
            ret.l10n_mx_edi_cfdi = datas
            cfdi = base64.decodebytes(datas).replace(
                b'xmlns:schemaLocation', b'xsi:schemaLocation')
            tree = ret.l10n_mx_edi_get_xml_etree(cfdi)
            # if already signed, extract uuid
            tfd_node = ret.l10n_mx_edi_get_tfd_etree(tree)
            if tfd_node is not None:
                ret.l10n_mx_edi_cfdi_uuid = tfd_node.get('UUID')

            ret.l10n_mx_edi_cfdi_issuing_rfc = tree.Emisor.get('RFCEmisor')

            if tree.Receptor.get('Nacionalidad') == 'Extranjero':
                ret.l10n_mx_edi_cfdi_receptor_rfc = tree.Receptor.Extranjero.get(
                    'NumRegIdTrib')
            else:
                ret.l10n_mx_edi_cfdi_receptor_rfc = tree.Receptor.Nacional.get(
                    'RFCRecep')
            certificate = tree.get('NumCert')
            ret.l10n_mx_edi_cfdi_certificate_id = self.env[
                'l10n_mx_edi.certificate'].sudo().search(
                [('serial_number', '=', certificate)], limit=1)

    @api.constrains('retentions_detail_ids', 'retentions_detail_ids.retained_amount')
    def _compute_required_amount(self):
        for ret in self:
            total_ret = 0
            for line in ret.retentions_detail_ids:
                total_ret += line.retained_amount
            ret.required_amount = total_ret

    @api.model
    def l10n_mx_edi_get_pac_version(self):
        return '1.0'

    # -------------------------------------------------------------------------
    # SAT/PAC service methods
    # -------------------------------------------------------------------------

    @api.model
    def _l10n_mx_edi_comdig_info(self, company_id, service_type):
        test = company_id.l10n_mx_edi_pac_test_env
        username = company_id.l10n_mx_edi_pac_username
        password = company_id.l10n_mx_edi_pac_password
        if service_type == 'sign':
            url = 'https://pruebas.comercio-digital.mx/timbre/timbrarV5.aspx'\
                if test else 'https://ws.comercio-digital.mx/timbre/timbrarV5.aspx'
        elif service_type == 'cancel':
            url = 'https://pruebas.comercio-digital.mx/cancela3/cancelarUuid'\
                if test else 'https://cancela.comercio-digital.mx/cancela3/cancelarUuid'
        elif service_type == 'check':
            url = 'https://cancela.comercio-digital.mx/arws/consultaEstatus'
        else:
            raise exceptions.UserError(_(
                'Invalid given service type for Comercio Digital'))
        return {
            'url': url,
            'multi': False,
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

        for ret in self:
            cfdi = base64.b64decode(ret.l10n_mx_edi_cfdi).decode('UTF-8')

            headers = {
                'Content-Type': 'text/xml',
                'usrws': username,
                'pwdws': password}
            try:
                response = requests.request(
                    'POST', url, data=cfdi, headers=headers, verify=False)
            except Exception as exc:
                err = exc + ' xml: ' + cfdi
                raise exceptions.UserError(_(
                    'Error during the process: %s') % err)

            code = _(tools.ustr(response.headers['codigo']))
            msg = ''
            if code and\
               code != '000':
                msg = _(tools.ustr(response.headers['errmsg']))
                msg = msg + ' xml: ' + cfdi

            xml_signed = response.content.decode('UTF-8')

            if xml_signed:
                xml_signed = base64.b64encode(xml_signed.encode('utf-8'))

            ret._l10n_mx_edi_post_sign_process(
                xml_signed if xml_signed else None, code, msg)

    @api.multi
    def _l10n_mx_edi_comdig_cancel(self, pac_info):
        '''CANCEL for Comercio digital.
        '''
        cadena_data = {
            'url': pac_info['url'],
            'username': pac_info['username'],
            'password': pac_info['password'],
            'tipoc': "R",
        }
        cadenacancela1 = "RFCE={0}\nUSER={1}\nPWDW={2}\nUUID={3}\nCERT={4}"
        cadenacancela2 = "\nRFCR={5}\nTIPOC={6}\nTOTAL={7}\nEMAILE={8}\nEMAILR={9}"
        cadenacancela3 = "\nKEYF={10}\nPWDK={11}\nACUS=SI\nTIPO=reten1.0"
        cadenacancela = cadenacancela1 + cadenacancela2 + cadenacancela3

        for ret in self:
            certificate_id = ret.company_id.l10n_mx_edi_certificate_ids.sudo(
            ).get_valid_certificate()

            cadena_data['uuids'] = ret.l10n_mx_edi_cfdi_uuid
            cadena_data['cer_pem'] = base64.encodebytes(
                certificate_id.get_pem_cer(
                    certificate_id.content)).decode('UTF-8')
            cadena_data['key_pem'] = base64.encodebytes(
                certificate_id.get_pem_key(
                    certificate_id.key,
                    certificate_id.password)).decode('UTF-8')
            cadena_data['key_password'] = certificate_id.password

            cadena_data['data'] = cadenacancela.format(
                ret.company_id.partner_id.vat,
                cadena_data['username'],
                cadena_data['password'],
                cadena_data['uuids'],
                cadena_data['cer_pem'].replace('\n', ''),
                ret.l10n_mx_edi_cfdi_receptor_rfc,
                cadena_data['tipoc'],
                "%.2f" % ret.operation_amount,
                'sistemas@gebesa.com',
                'sistemas@gebesa.com',
                cadena_data['key_pem'].replace('\n', ''),
                cadena_data['key_password']).encode()
            try:
                req = {
                    'request': urllib.request.Request(
                        url=cadena_data['url'],
                        data=cadena_data['data'],
                        headers={'Content-Type': 'text/plain'})
                }
            except Exception as exc:
                req['errmsge'] = str(exc) + 'uuids: ' + cadena_data['uuids'] +\
                    'rfc cliente: ' + ret.l10n_mx_edi_cfdi_receptor_rfc +\
                    'rfc emisor: ' + ret.company_id.partner_id.vat +\
                    'total: ' + "%.2f" % ret.operation_amount +\
                    'tipoc: ' + cadena_data['tipoc']
                raise exceptions.UserError(_(
                    'Error during the process: %s') % req['errmsge'])

            with urllib.request.urlopen(req['request']) as response:
                req['response_text'] = response.read()
                try:
                    if req['response_text'] == b'':
                        req['errmsge'] = response.headers['errmsg']
                        raise exceptions.UserError(_(
                            'Error during the process: %s'
                        ) % req['errmsge'] + " data: " + cadena_data[
                            'data'].decode())

                    xml = {
                        'xml': minidom.parseString(req['response_text'])
                    }
                except Exception as exc:
                    raise exceptions.UserError(_(
                        'Error during the process: %s') % str(exc))

            xml['estatusuuid'] = xml[
                'xml'].documentElement.getElementsByTagName(
                    "EstatusUUID")[0].firstChild.nodeValue
            xml['uuids'] = xml[
                'xml'].documentElement.getElementsByTagName(
                    "UUID")[0].firstChild.nodeValue

            # cancelled or previously cancelled
            xml['cancelled'] = str(xml['estatusuuid']) in ('201', '202')
            if xml['cancelled']:
                self.env['ir.attachment'].with_context({}).create(
                    {
                        'name': 'acuse_cancelacion_' + xml['uuids'] + '.xml',
                        'datas': base64.encodebytes(
                            req['response_text'] and req[
                                'response_text'] or ''),
                        'datas_fname': 'acuse_cancelacion_' + xml['uuids'] + '.xml',
                        'description': _(
                            'XML Acuse de cancelacion de: %s.' % ret.number),
                        'res_model': ret._name,
                        'res_id': ret.id,
                    }
                )
            # no show code and response message if cancel was success
            msg = '' if xml['cancelled'] else _(
                ' Cfdi No encontrado o no corresponde al emisor.\n- El uuid'
                ' es:') + xml['uuids']
            code = '' if xml['cancelled'] else str(xml['estatusuuid'])
            ret._l10n_mx_edi_post_cancel_process(xml['cancelled'], code, msg)

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
            raise exceptions.UserError(_(
                'The sign service requested failed') + extend)
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
            raise exceptions.UserError(_(
                'The cancel service requested failed') + extend)
        post_msg = []
        if code:
            post_msg.extend([_('Code: %s') % code])
        if msg:
            post_msg.extend([_('Message: %s') % msg])
        self.message_post(
            body=body_msg + create_list_html(post_msg))

    def l10n_mx_edi_append_addenda(self, xml_signed):
        self.ensure_one()
        addenda = self.partner_id.l10n_mx_edi_addenda or\
            self.partner_id.commercial_partner_id.l10n_mx_edi_addenda
        if not addenda:
            return xml_signed
        values = {
            'record': self,
        }
        addenda_node_str = addenda.render(values=values).strip()
        if not addenda_node_str:
            return xml_signed
        tree = fromstring(base64.decodebytes(xml_signed))
        addenda_node = fromstring(addenda_node_str)
        if addenda_node.tag != '{http://www.sat.gob.mx/cfd/3}Addenda':
            node = etree.Element(etree.QName(
                'http://www.sat.gob.mx/cfd/3', 'Addenda'))
            node.append(addenda_node)
            addenda_node = node
        tree.append(addenda_node)
        self.message_post(
            body=_('Addenda has been added in the CFDI with success'),
            subtype='account.mt_invoice_validated')
        xml_signed = base64.encodebytes(etree.tostring(
            tree, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
        attachment_id = self.l10n_mx_edi_retrieve_last_attachment()
        attachment_id.write({
            'datas': xml_signed,
            'mimetype': 'application/xml'
        })
        return xml_signed

    @api.model
    def l10n_mx_edi_retrieve_attachments(self):
        '''Retrieve all the cfdi attachments generated for this retention.

        :return: An ir.attachment recordset
        '''
        self.ensure_one()
        if not self.l10n_mx_edi_cfdi_name:
            return []
        domain = [
            ('res_id', 'in', self.ids),
            ('res_model', '=', self._name),
            ('name', '=', self.l10n_mx_edi_cfdi_name)]
        return self.env['ir.attachment'].search(domain)

    @api.model
    def l10n_mx_edi_retrieve_last_attachment(self):
        attachment_ids = self.l10n_mx_edi_retrieve_attachments()
        return attachment_ids[0] if attachment_ids else None

    @api.model
    def l10n_mx_edi_get_xml_etree(self, cfdi=None):
        '''Get an objectified tree representing the cfdi.
        If the cfdi is not specified, retrieve it from the attachment.

        :param cfdi: The cfdi as string
        :return: An objectified tree
        '''
        self.ensure_one()
        if cfdi is None and self.l10n_mx_edi_cfdi:
            cfdi = base64.decodebytes(self.l10n_mx_edi_cfdi)
        return fromstring(cfdi) if cfdi else None

    @api.model
    def l10n_mx_edi_get_tfd_etree(self, cfdi):
        '''Get the TimbreFiscalDigital node from the cfdi.

        :param cfdi: The cfdi as etree
        :return: the TimbreFiscalDigital node
        '''
        if not hasattr(cfdi, 'Complemento'):
            return None
        attribute = 'tfd:TimbreFiscalDigital[1]'
        namespace = {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}
        node = cfdi.Complemento.xpath(attribute, namespaces=namespace)
        return node[0] if node else None

    @api.model
    def _get_l10n_mx_edi_cadena(self):
        self.ensure_one()
        # get the xslt path
        xslt_path = CFDI_XSLT_CADENA_TFD
        # get the cfdi as eTree
        cfdi = base64.decodebytes(self.l10n_mx_edi_cfdi)
        cfdi = self.l10n_mx_edi_get_xml_etree(cfdi)
        cfdi = self.l10n_mx_edi_get_tfd_etree(cfdi)
        # return the cadena
        return self.l10n_mx_edi_generate_cadena(xslt_path, cfdi)

    # @run_after_commit
    @api.multi
    def _l10n_mx_edi_call_service(self, service_type):
        '''Call the right method according to the pac_name, it's info returned by the '_l10n_mx_edi_%s_info' % pac_name'
        method and the service_type passed as parameter.
        :param service_type: sign or cancel
        '''
        # Regroup the retentions by company (= by pac)
        comp_x_records = groupby(self, lambda r: r.company_id)
        for company_id, records in comp_x_records:
            pac_name = company_id.l10n_mx_edi_pac
            if not pac_name:
                continue
            # Get the informations about the pac
            pac_info_func = '_l10n_mx_edi_%s_info' % pac_name
            service_func = '_l10n_mx_edi_%s_%s' % (pac_name, service_type)
            pac_info = getattr(self, pac_info_func)(company_id, service_type)
            # Call the service with retentions one by one or all together according to the 'multi' value.
            multi = pac_info.pop('multi', False)
            if multi:
                # rebuild the recordset
                records = self.env['l10n_mx_edi.retentions'].search(
                    [('id', 'in', self.ids), ('company_id', '=', company_id.id)])
                getattr(records, service_func)(pac_info)
            else:
                for record in records:
                    getattr(record, service_func)(pac_info)

    @api.multi
    def _l10n_mx_edi_sign(self):
        '''Call the sign service with records that can be signed.
        '''
        records = self.search([
            ('l10n_mx_edi_pac_status', 'not in', ['signed', 'to_cancel', 'cancelled', 'retry']),
            ('id', 'in', self.ids)])
        records._l10n_mx_edi_call_service('sign')

    @api.model
    def l10n_mx_edi_generate_cadena(self, xslt_path, cfdi_as_tree):
        '''Generate the cadena of the cfdi based on an xslt file.
        The cadena is the sequence of data formed with the information contained within the cfdi.
        This can be encoded with the certificate to create the digital seal.
        Since the cadena is generated with the retention data, any change in it will be noticed resulting in a different
        cadena and so, ensure the retention has not been modified.

        :param xslt_path: The path to the xslt file.
        :param cfdi_as_tree: The cfdi converted as a tree
        :return: A string computed with the retention data called the cadena
        '''
        xslt_root = etree.parse(tools.file_open(xslt_path))
        return str(etree.XSLT(xslt_root)(cfdi_as_tree))

    @api.model
    def create(self, vals_list):
        if vals_list.get('number', 'New') == 'New':
            vals_list['number'] = self.env['ir.sequence'].next_by_code(
                'l10n_mx_edi.retentions') or '/'
        return super().create(vals_list)

    @api.multi
    def _l10n_mx_edi_create_cfdi_values(self):
        values = {
            'record': self,
        }
        return values

    @api.multi
    def _l10n_mx_edi_create_cfdi(self):
        error_log = []
        pac_name = self.company_id.l10n_mx_edi_pac

        values = self._l10n_mx_edi_create_cfdi_values()
        values['date'] = fields.Datetime.context_timestamp(
            self, self.date).strftime('%Y-%m-%dT%H:%M:%S-06:00')

        values['nationality'] = 'Nacional'
        if self.partner_id.country_id != self.env.ref('base.mx'):
            values['nationality'] = 'Extranjero'
        # -----------------------
        # Check the configuration
        # -----------------------
        # -Check certificate
        certificate_ids = self.company_id.l10n_mx_edi_certificate_ids
        certificate_id = certificate_ids.sudo().get_valid_certificate()
        if not certificate_id:
            error_log.append(('No valid certificate found'))

        # -Check PAC
        if pac_name:
            pac_test_env = self.company_id.l10n_mx_edi_pac_test_env
            pac_password = self.company_id.l10n_mx_edi_pac_password
            if not pac_test_env and not pac_password:
                error_log.append(('No PAC credentials specified.'))
        else:
            error_log.append(('No PAC specified.'))

        if error_log:
            return {
                'error': ('Please check your configuration: ') + create_list_html(error_log)}

        values['certificate_number'] = certificate_id.serial_number
        values['certificate'] = certificate_id.sudo().get_data()[0]

        # import ipdb; ipdb.set_trace()
        cfdi = self.env['ir.qweb'].render(CFDI_TEMPLATE_10, values=values)
        cfdi = cfdi.replace(b'xmlns__', b'xmlns:')
        node_sello = 'Sello'

        # -Compute cadena
        version = self.l10n_mx_edi_get_pac_version()
        tree = self.l10n_mx_edi_get_xml_etree(cfdi)
        cadena = self.l10n_mx_edi_generate_cadena(CFDI_XSLT_CADENA % version, tree)
        tree.attrib[node_sello] = certificate_id.sudo().get_encrypted_cadena_retention(cadena)

        res = {'cfdi': b'<?xml version="1.0" encoding="UTF-8"?>' + etree.tostring(tree)}
        return res

    @api.multi
    def _l10n_mx_edi_retry(self):
        version = self.l10n_mx_edi_get_pac_version()
        for ret in self:
            cfdi_values = ret._l10n_mx_edi_create_cfdi()
            error = cfdi_values.pop('error', None)
            cfdi = cfdi_values.pop('cfdi', None)

            if error:
                # cfdi failed to be generated
                ret.l10n_mx_edi_pac_status = 'retry'
                ret.message_post(body=error, subtype='account.mt_invoice_validated')
                continue
            # cfdi has been successfully generated
            ret.l10n_mx_edi_pac_status = 'to_sign'

            filename = ('%s-MX-Retention-%s.xml' % (
                ret.number, version.replace('.', '-'))).replace('/', '')

            ret.l10n_mx_edi_cfdi_name = filename
            attachment_id = self.env['ir.attachment'].create({
                'name': filename,
                'res_id': ret.id,
                'res_model': ret._name,
                'datas': base64.encodebytes(cfdi),
                'datas_fname': filename,
                'description': 'Mexican retention',
            })
            ret.message_post(
                body='CFDI document generated (may be not signed)',
                attachment_ids=[attachment_id.id],
                subtype='account.mt_invoice_validated')
            ret._l10n_mx_edi_sign()

    @api.multi
    def _l10n_mx_edi_cancel(self):
        '''Call the cancel service with records that can be signed.
        '''
        records = self.search([
            ('l10n_mx_edi_pac_status', 'in', [
                'to_sign', 'signed', 'to_cancel', 'retry']),
            ('id', 'in', self.ids)])
        for record in records:
            if record.l10n_mx_edi_pac_status in ['to_sign', 'retry']:
                record.l10n_mx_edi_pac_status = False
                record.message_post(body=_(
                    'The cancel service has been called with success'))
            else:
                record.l10n_mx_edi_pac_status = 'to_cancel'
        records = self.search([
            ('l10n_mx_edi_pac_status', '=', 'to_cancel'),
            ('id', 'in', self.ids)])
        records._l10n_mx_edi_call_service('cancel')

    @api.multi
    def action_validate(self):
        for retention in self:
            retention._l10n_mx_edi_retry()
            retention.state = 'valid'

    @api.multi
    def action_cancel(self):
        for retention in self:
            retention._l10n_mx_edi_cancel()
            retention.state = 'cancel'


class L10nMxEdiRetentionTaxes(models.Model):
    _name = 'l10n_mx_edi.retentions.taxes'
    _description = "Retention Lines"

    retention_type = fields.Selection([
        ('final', 'Final payment'),
        ('provisional', 'Provisional payment'), ],
        string='Retention type',
    )
    retained_amount = fields.Float(
        string="Retained amount",
        required=True
    )
    tax = fields.Selection([
        ('01', 'ISR'),
        ('02', 'IVA'),
        ('03', 'IEPS'), ],
        string='Tax',
    )
    base_amount = fields.Float(
        string="Base amount",
        required=True
    )
    retentions_id = fields.Many2one(
        'l10n_mx_edi.retentions',
        string="Retentions"
    )
