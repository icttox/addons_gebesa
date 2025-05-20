# -*- coding: utf-8 -*-

import traceback
from lxml.objectify import fromstring
# from xml.dom.minidom import parseString
import requests
from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError


class HrEmployeeMedicalExpense(models.Model):
    _name = "hr.employee.medical.expense"
    _inherit = ['message.post.show.all']
    _description = "Employee Medical Expense"
    _order = 'name asc'
    _rec_name = 'name'

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        required=True
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda s: s.env.user.company_id,
    )

    name = fields.Char(
        string='Name',
        size=250,
        required=True,
        index=True,
        copy=False,
        default='New',
        track_visibility='always')

    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('authorized', 'Validated'),
            ('refund', 'Refund'),
            ('cancel', 'Cancel')],
        string='Status',
        readonly=True,
        default='draft',
    )

    date_capture = fields.Date(
        string='Date Capture',
    )

    date_cfdi = fields.Date(
        string='Date CFDI',
    )

    supplier = fields.Char(
        string='Proveedor',
        size=250,
        required=True)

    rfc_supplier = fields.Char(
        string='RFC Proveedor',
        size=250,
        required=True)

    total = fields.Float(
        string='Total',
    )

    uuid = fields.Char(
        string='UUID',
        size=250,
        required=True)

    supplier_folio = fields.Char(
        string='Supplier Folio',
        size=250,
        required=True)

    authorized = fields.Boolean(
        string='Authorized',
    )

    refund = fields.Boolean(
        string='Refund',
    )

    method_payment = fields.Char(
        string='Method Payment',
        size=250,
        required=True)

    use_cfdi = fields.Char(
        string='Use CFDI',
        size=250,
        required=True)

    medical_expense_line_ids = fields.One2many(
        'hr.employee.medical.expense.line',
        'medicalexp_id',
        string="Employee Medical Expense Line"
    )

    _sql_constraints = [
        ('uuid_uniq', 'unique (uuid)',
         'Este Gasto Médico ya existe en el sistema.')
    ]

    @api.model
    def create(self, vals_list):
        vals_list['name'] = self.env['ir.sequence'].next_by_code(
            'hr.employee.medical.expense') or '/'
        medical = super().create(vals_list)
        if self.env.context.get('check_sat', True):
            estatus = medical._validate_xml_sat(
            medical.rfc_supplier, medical.employee_id.rfc,
            medical.total, medical.uuid)
            if estatus not in('vigente', 'Vigente'):
                raise ValidationError(_('This CFDi isn\'t in the SAT\'s records: %s' % estatus + ' - ' + medical.uuid))
        return medical

    # @api.multi
    # def action_validations(self):
    #     for expense in self:
    #         if expense.uuid == expense.uuid:
    #             raise UserError(_("Check your expenses. They should not be the same."))

    @api.multi
    def action_validate(self):
        for expense in self:
            expense.status = 'authorized'
            if expense.status == 'authorized':
                expense.authorized = True
            return True

    @api.multi
    def action_refund(self):
        for expense in self:
            expense.status = 'refund'
            if expense.status == 'refund':
                expense.refund = True
            return True

    @api.multi
    def action_cancel(self):
        for expense in self:
            expense.status = 'cancel'
            if expense.status == 'cancel':
                expense.authorized = False
                expense.refund = False
            return True

    @api.multi
    def _validate_xml_sat(self, vat_emitter, vat_receiver, amount, uuid):
        """Validate XML state in SAT system"""
        url = 'https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc?wsdl'
        headers = {'SOAPAction': 'http://tempuri.org/IConsultaCFDIService/Consulta', 'Content-Type': 'text/xml; charset=utf-8'}
        template = """<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:ns0="http://tempuri.org/" xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
   <SOAP-ENV:Header/>
   <ns1:Body>
      <ns0:Consulta>
         <ns0:expresionImpresa>${data}</ns0:expresionImpresa>
      </ns0:Consulta>
   </ns1:Body>
</SOAP-ENV:Envelope>"""
        namespace = {'a': 'http://schemas.datacontract.org/2004/07/Sat.Cfdi.Negocio.ConsultaCfdi.Servicio'}

        params = '?re=%s&amp;rr=%s&amp;tt=%s&amp;id=%s' % (
            tools.html_escape(tools.html_escape(vat_emitter or '')),
            tools.html_escape(tools.html_escape(vat_receiver or '')),
            amount or 0.0, uuid or '')
        soap_env = template.format(data=params)
        try:
            soap_xml = requests.post(
                url, data=soap_env, headers=headers, timeout=20)
            response = fromstring(soap_xml.text)
            status = response.xpath(
                '//a:Estado', namespaces=namespace)
        except Exception:
            error = tools.ustr(traceback.format_exc())
            raise ValidationError(_(
                'An error has ocurred while connecting to the SAT '
                'validation service: %s' % error))
        return status[0] if status else 'none'

    #     url = 'https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc?wsdl'  # noqa
    #     data = _('?re=%s&rr=%s&tt=%s&id=%s' % (vat_emitter, vat_receiver, amount, uuid))
    #     msg = "<soapenv:Envelope xmlns:soapenv='http://schemas.xmlsoap.org/"
    #     msg += "soap/envelope/' "
    #     msg += "xmlns:tem='http://tempuri.org/'>"
    #     msg += "<soapenv:Header/>"
    #     msg += "<soapenv:Body>"
    #     msg += "<tem:Consulta>"
    #     msg += "<tem:expresionImpresa><![CDATA["
    #     msg += data
    #     msg += "]]></tem:expresionImpresa>"
    #     msg += "</tem:Consulta>"
    #     msg += "</soapenv:Body>"
    #     msg += "</soapenv:Envelope>"

    #     headers = {
    #         'content-type': 'text/xml; charset=utf-8',
    #         'Accept': 'text/xml',
    #         'soapaction': "http://tempuri.org/IConsultaCFDIService/Consulta",
    #         'cache-control': "no-cache",
    #         'Host': "consultaqr.facturaelectronica.sat.gob.mx"
    #     }

    #     codstatus = 'unknown'
    #     try:
    #         response = requests.request(
    #             "POST",
    #             url,
    #             data=msg,
    #             headers=headers
    #         )

    #         resultados_mensaje = response.content
    #         dom = parseString(resultados_mensaje)
    #         codstatus = dom.getElementsByTagName(
    #             'a:Estado')[0].firstChild.nodeValue

    #     except Exception as e:
    #         error = tools.ustr(traceback.format_exc())
    #         raise ValidationError(_(
    #             'An error has ocurred while connecting to the SAT '
    #             'validation service: %s' % error))
    #     return codstatus
