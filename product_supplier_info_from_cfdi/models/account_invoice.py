# -*- coding: utf-8 -*-
# Copyright 2019, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from codecs import BOM_UTF8
from odoo import api, models
from odoo.exceptions import UserError
from lxml import objectify

BOM_UTF8U = BOM_UTF8.decode('UTF-8')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def get_product_supplierinfo_cfdi(self):
        for invoice in self:
            if invoice.xml_signed:
                xml = objectify.fromstring(
                    invoice.xml_signed.lstrip(BOM_UTF8U).encode("UTF-8"))
                for concept in xml.Conceptos:
                    code = concept.Concepto.get('NoIdentificacion')
                    qty = concept.Concepto.get('Cantidad')
                    desc = concept.Concepto.get('Descripcion')
                    # amnt = concept.get('Importe')
                    # uom = concept.get('Unidad')
                    # codeuom = concept.get('ClaveUnidad')
                    # codesat = concept.get('ClaveProdServ')
                    unitprice = concept.Concepto.get('ValorUnitario')
                    descto = unitprice = concept.Concepto.get('Descuento') or 0.00
                    desctouni = descto / qty
                    unitprice = unitprice - desctouni

                    if not qty or not unitprice:
                        continue

                    line = invoice.invoice_line_ids.filtered(
                        lambda x: (
                            x.quantity == float(qty) and x.price_unit == float(unitprice)) and x.product_id or False)
                    if not line:
                        continue

                    if len(line) > 1:
                        continue

                    if line.product_id.type != u'product':
                        continue

                    suppinf = self.env['product.supplierinfo'].search(
                        [('name', '=', invoice.partner_id.id),
                         ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id)])

                    if suppinf:
                        suppinf.write(
                            {'product_code': code,
                             'product_name': desc,
                             'price': unitprice})
                    else:
                        suppinf.create(
                            {'product_code': code,
                             'product_name': desc,
                             'price': unitprice,
                             'name': invoice.partner_id.id,
                             'product_tmpl_id': line.product_id.product_tmpl_id.id}
                        )
            else:
                raise UserError('Favor de primero adjuntar el CFDI')
