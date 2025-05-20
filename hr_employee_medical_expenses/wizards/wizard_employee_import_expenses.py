# -*- coding: utf-8 -*-
# © 2021 Leslie Marquez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import datetime
import base64
from xml.dom.minidom import parseString
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ExpenseImportCfdi(models.TransientModel):
    _name = 'expense.import.cfdi'
    _description = 'descripcion pendiente'

    cfdi = fields.Binary(
        string='CFD-I',
        filters='*.xml'
    )

    state = fields.Selection(
        [('init', 'init'),
         ('ready', 'ready'),
         ('error', 'error')],
        string="State",
        default='init',
    )

    check_sat = fields.Boolean(
        string="Check SAT",
        default=True,
    )

    xml_name = fields.Char(help='Stores the XML File\'s name')

    pdf_name = fields.Char(help='Stores the PDF File\'s name')

    file_pdf = fields.Binary(help='This is the PDF file that you vendor provides you')

    @api.multi
    def import_cfdi(self):
        attachment_obj = self.env['ir.attachment']
        medicalexp_obj = self.env['hr.employee.medical.expense']
        medicalexp_line_obj = self.env['hr.employee.medical.expense.line']
        ctxt = self._context.copy()
        ctxt['check_sat'] = self.check_sat
        for cfdi_import in self:
            cfdi = cfdi_import.cfdi
            cfdi_data = base64.decodebytes(cfdi)
            dom = parseString(cfdi_data)
            file_pdf = cfdi_import.file_pdf
            supplier_folio = 'SinFolio'

            timbre_fiscal = dom.getElementsByTagName('tfd:TimbreFiscalDigital')
            emisor = dom.getElementsByTagName('cfdi:Emisor')
            comprobante = dom.getElementsByTagName('cfdi:Comprobante')
            receptor = dom.getElementsByTagName('cfdi:Receptor')
            conceptos = dom.getElementsByTagName('cfdi:Concepto')
            if 'Folio' in comprobante[0].attributes.keys():
                supplier_folio = comprobante[0].attributes['Folio'].value or False
            uuid = timbre_fiscal[0].attributes['UUID'].value or False
            rfc_emisor = emisor[0].attributes['Rfc'].value or False
            rfc_receptor = receptor[0].attributes['Rfc'].value or False
            amount_cfdi = comprobante[0].attributes['Total'].value or False
            cfdi_date = timbre_fiscal[0].attributes['FechaTimbrado'].value or False
            supplier = emisor[0].attributes['Nombre'].value or False
            met_pago = comprobante[0].attributes['MetodoPago'].value or False
            use_cfdi = receptor[0].attributes['UsoCFDI'].value or False
            date = datetime.datetime.now()
            employee_obj = self.env['hr.employee']
            employee = employee_obj.search([('rfc', '=', rfc_receptor)])
            if not employee:
                raise ValidationError(_('No se encuentra un empleado con ese RFC.'))
            if len(employee) > 1:
                raise ValidationError(_(
                    'Mas de un empleado tiene el rfc %s' % rfc_receptor))
            medical = medicalexp_obj.with_context(ctxt).create({
                'employee_id': employee.id,
                'date_capture': date,
                'date_cfdi': cfdi_date,
                'supplier': supplier,
                'rfc_supplier': rfc_emisor,
                'total': amount_cfdi,
                'uuid': uuid,
                'use_cfdi': use_cfdi,
                'supplier_folio': supplier_folio,
                'refund': False,
                'authorized': False,
                'method_payment': met_pago,
            })

            for concept in conceptos:
                descrip = concept.getAttribute("Descripcion") or False
                unit = concept.getAttribute("Unidad") or False
                if not concept.getAttribute("Unidad") or False:
                    unit = 'N/A'
                quant = concept.getAttribute("Cantidad") or False
                price_unit = concept.getAttribute("ValorUnitario") or False
                total = concept.getAttribute("Importe") or False
                prod_serv = concept.getAttribute("ClaveProdServ") or False
                prod_sat_obj = self.env['l10n_mx_edi.product.sat.code']
                sat_prod = prod_sat_obj.search([('code', '=', prod_serv)])
                if not sat_prod:
                    raise ValidationError(_('No se encuentra la clave servicio del SAT.'))
                medicalexp_line_obj.create({
                    'medicalexp_id': medical.id,
                    'product_sat_code_id': sat_prod.id,
                    'description': descrip,
                    'unit': unit,
                    'quantity': quant,
                    'price_unit': price_unit,
                    'total': total
                })

            if uuid is False or rfc_emisor is False or \
                    amount_cfdi is False:
                error = _(u"The xml does not have a UUID attribute, " "rfc receiver or a total")
                raise ValidationError(_(error))

            ctx = dict(self._context)
            ctx.pop('default_type', None)

            attachment_name = rfc_emisor
            attachment_name = attachment_name + '/' + supplier_folio
            attachment_obj.with_context(ctx).create({
                'name': attachment_name + '.xml',
                'datas': cfdi,
                'datas_fname': attachment_name + '.xml',
                'res_model': 'hr.employee.medical.expense',
                'res_id': medical.id
            })

            attachment_obj.with_context(ctx).create({
                'name': attachment_name + '.pdf',
                'datas': file_pdf,
                'datas_fname': attachment_name + '.pdf',
                'res_model': 'hr.employee.medical.expense',
                'res_id': medical.id
            })

        return {
            'name': _('Medical Expenses'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.employee.medical.expense',
            'view_id': False,
            'domain': [('id', 'in', medical.ids)],
        }
