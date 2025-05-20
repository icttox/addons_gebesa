# -*- coding: utf-8 -*-
# © 2019 Samuel Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from xml.dom.minidom import parseString
from odoo import api, models


class InvoiceImportCfdi(models.Model):
    _inherit = 'invoice.import.cfdi'

    @api.multi
    def import_cfdi(self):
        super().import_cfdi()
        invoice_obj = self.env['account.invoice']
        invoice_line_obj = self.env['account.invoice.line']
        supplierinfo_obj = self.env['product.supplierinfo']
        sat_code_obj = self.env['l10n_mx_edi.product.sat.code']
        uom_obj = self.env['uom.uom']
        invoice_ids = self._context.get('active_id', False)
        for invoice in invoice_obj.browse(invoice_ids):
            if invoice.invoice_line_ids:
                continue
            for cfdi_import in self:
                cfdi = cfdi_import.cfdi
                cfdi_data = base64.decodebytes(cfdi)
                dom = parseString(cfdi_data)
                comprobante = dom.getElementsByTagName('cfdi:Comprobante')
                if 'Folio' in comprobante[0].attributes.keys():
                    invoice.write({'reference': comprobante[0].attributes['Folio'].value})
                conceptos = dom.getElementsByTagName('cfdi:Conceptos')
                for concepto in conceptos[0].getElementsByTagName('cfdi:Concepto'):
                    code = concepto.attributes['NoIdentificacion'].value or False
                    description = concepto.attributes['Descripcion'].value or False
                    qty = concepto.attributes['Cantidad'].value or False
                    price_unit = concepto.attributes['ValorUnitario'].value or False
                    uom = concepto.attributes['ClaveUnidad'].value or False
                    product = False
                    if code:
                        product = supplierinfo_obj.search([
                            ('name', '=', invoice.partner_id.id),
                            ('product_code', '=', code)])
                        if product.product_id:
                            product = product.product_id
                        elif product.product_tmpl_id:
                            if product.product_tmpl_id.product_variant_count == 1:
                                product = product.product_tmpl_id.product_variant_ids[0]
                    line = invoice_line_obj.create({
                        'product_id': product.id,
                        'name': description,
                        'account_id': invoice.account_id.id,
                        'price_unit': price_unit,
                        'quantity': qty,
                        'invoice_id': invoice.id,
                        'account_analytic_id': invoice.account_analytic_id.id
                    })

                    if product:
                        line._onchange_product_id()
                        line._onchange_account_id()
                        # line._onchange_uom_id()

                    uom_id = False
                    code_sat = sat_code_obj.search([
                        ('code', '=', uom),
                        ('active', '=', 1)], limit=1)
                    if code_sat:
                        uom_id = uom_obj.search([
                            ('l10n_mx_edi_code_sat_id', '=', code_sat.id),
                            ('active', '=', 1)], limit=1).id
                    line.write({'uom_id': uom_id})

            invoice.compute_taxes()
