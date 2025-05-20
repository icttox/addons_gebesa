# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import os
from base64 import b64decode

try:
    import xlrd
except ImportError:
    xlrd = None

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import pycompat


class SaleOrderImport(models.TransientModel):
    _name = "sale.order.import"
    _description = "Sale Order Import"

    data = fields.Binary('File', required=True)
    filename = fields.Char('File Name', required=True)

    @api.multi
    def import_order(self):
        context = self.env.context or {}
        active_model = context.get('active_model', False)
        active_id = context.get('active_id', False)

        sale_order = self.env['sale.order']
        if active_model == 'sale.order' and active_id:
            sale_order = sale_order.browse(active_id)
        if not sale_order or sale_order.state not in ('draft', 'sent'):
            raise UserError(_('Sale order state not in (draft, sent)!!'))

        product_obj = self.env['product.product']
        tax_obj = self.env['account.tax']
        this = self[0]

        fileformat = os.path.splitext(this.filename)[-1][1:].lower()
        if fileformat != 'xls':
            raise UserError(_('Valid format is .xls'))
        book = xlrd.open_workbook(file_contents=b64decode(self.data))
        sheet = book.sheet_by_index(0)
        order_line = []
        is_int = isinstance(sheet.nrows, pycompat.integer_types)
        nrows = sheet.nrows if (is_int and sheet.nrows > 0) else 0
        for row in pycompat.imap(sheet.row, range(1, nrows)):
            domain = [('default_code', '=ilike', row[0].value)]
            product = product_obj.search(domain, limit=1)
            if not product:
                raise UserError(
                    _('Error, no existe el producto: %s') % row[0].value)

            product = product.with_context(
                lang=sale_order.partner_id.lang,
                partner=sale_order.partner_id,
                quantity=row[1].value,
                date=sale_order.date_order,
                pricelist=sale_order.pricelist_id.id,
                uom=product.uom_id.id
            )

            name = self.env['sale.order.line'].get_sale_order_line_multiline_description_sale(product)

            domain = [('type_tax_use', '=', 'sale'),
                      ('name', '=ilike', row[4].value)]
            tax = tax_obj.search(domain, limit=1)
            sol_values = {
                'name': name,
                'product_uom': product.uom_id.id,
                'product_id': product.id,
                'tax_id': [(6, 0, [tax.id])] if tax else False,
                'price_unit': row[2].value,
                'product_uom_qty': row[1].value,
                'porce_desc': row[3].value,
                'line_tag_number': row[5].value,
                'margin_justification': row[6].value,
            }
            order_line.append((0, 0, sol_values))
        sale_order.order_line.unlink()
        sale_order.order_line = order_line

        for line in sale_order.order_line:
            line.product_id_change()
        return {}
