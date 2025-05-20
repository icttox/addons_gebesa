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


class ProductReplacementImport(models.TransientModel):
    _name = "product.replacement.import"
    _description = "Product Replacement Import"

    data = fields.Binary('File', required=True)
    filename = fields.Char('File Name', required=True)

    @api.multi
    def import_product_replacement(self):
        context = self.env.context or {}
        active_model = context.get('active_model', False)
        active_id = context.get('active_id', False)

        mrp_bom_line = self.env['mrp.bom.line']
        if active_model == 'mrp.bom.line' and active_id:
            mrp_bom_line = mrp_bom_line.browse(active_id)
        if not mrp_bom_line or not mrp_bom_line.bom_id:
            raise UserError(_('In order to import replacement products, '
                              'please save changes in the BoM'))

        # product_obj = self.env['product.product']
        # tax_obj = self.env['account.tax']
        this = self[0]

        fileformat = os.path.splitext(this.filename)[-1][1:].lower()
        if fileformat != 'xls':
            raise UserError(_('Valid format is .xls'))
        book = xlrd.open_workbook(file_contents=b64decode(self.data))
        sheet = book.sheet_by_index(0)
        bom_line_product_value_ids = []
        is_int = isinstance(sheet.nrows, pycompat.integer_types)
        nrows = sheet.nrows if (is_int and sheet.nrows > 0) else 0
        for row in pycompat.imap(sheet.row, range(1, nrows)):

            domain = [('default_code', '=ilike', row[0].value)]
            product_variant = self.env['product.product'].search(domain, limit=1)
            if not product_variant:
                raise UserError(
                    _('Error, no existe la variante del producto: %s') % row[0].value)

            if mrp_bom_line.bom_id.product_tmpl_id.id != product_variant.product_tmpl_id.id:
                raise UserError(_('Error, La variante del producto no pertenece al mismo producto padre que el BoM: %s') % row[0].value)

            domain = [('default_code', '=ilike', row[2].value)]
            product_replacement = self.env['product.product'].search(domain, limit=1)
            if not product_replacement:
                raise UserError(
                    _('Error, no existe el producto de reemplazo: %s') % row[2].value)

            # product = product.with_context(
            #     lang=mrp_bom_line.partner_id.lang,
            #     partner=mrp_bom_line.partner_id,
            #     quantity=row[1].value,
            #     date=mrp_bom_line.date_order,
            #     pricelist=mrp_bom_line.pricelist_id.id,
            #     uom=product.uom_id.id
            # )

            # name = self.env['sale.order.line'].get_sale_order_line_multiline_description_sale(product)

            # domain = [('type_tax_use', '=', 'sale'),
            #           ('name', '=ilike', row[4].value)]
            # tax = tax_obj.search(domain, limit=1)

            line_values = {
                'bom_line_value_id': mrp_bom_line.id,
                'bom_product_id': product_variant.id,
                'product_id': product_replacement.id,
            }
            bom_line_product_value_ids.append((0, 0, line_values))
        mrp_bom_line.bom_line_product_value_ids.unlink()
        mrp_bom_line.bom_line_product_value_ids = bom_line_product_value_ids

        # for line in mrp_bom_line.bom_line_product_value_ids:
        #     line.product_id_change()
        return {}
