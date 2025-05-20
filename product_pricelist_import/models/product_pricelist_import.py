# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    _sql_constraints = [
        ('register_unique',
         'UNIQUE (company_id,currency_id,product_id,pricelist_id,min_quantity,\
         applied_on)',
         'You can not have two item with the same companny, currency, product, \
          min quantity, applied !')
    ]


class ProductPricelistImport(models.Model):
    _name = 'product.pricelist.import'
    _description = 'Product Pricelist Import'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Code',
        required=True,
        size=64,
    )

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
    )

    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done'),
         ('cancel', 'Cancelled')],
        string='State',
        default='draft',
    )

    lines_ids = fields.One2many(
        'product.pricelist.import.line',
        'product_pricelist_import_id',
        string='Price import lines',
    )

    min_qty = fields.Float(
        string='Min Quantity',
        required=True,
    )

    @api.model
    def force_validate_draft(self):
        pending = self.env['product.pricelist.import'].search([
            ('state', '=', 'draft')])

        for rec in pending:
            rec.product_import()

    @api.multi
    def import_cancel(self):
        for impo in self:
            impo.write({'state': 'cancel'})

    @api.multi
    def product_import(self):
        # Diccionario de las listas de precios el valor
        # es una lista con el id de la lista de precios,
        # el id de la moneda, y el campo del precio
        pricelist = {
            'code_mx': [28, 34, 'price_mex'],
            'code_d00': [30, 34, 'price_d00'],
            'code_d001': [31, 34, 'price_d00_01'],
            'code_d01': [32, 34, 'price_d01'],
            'code_d02': [33, 34, 'price_d02'],
            'code_d03': [34, 34, 'price_d03'],
            'code_d04': [35, 34, 'price_d04'],
            'code_d05': [36, 34, 'price_d05'],
            'code_d06': [37, 34, 'price_d06'],
            'code_d07': [38, 34, 'price_d07'],
            'code_d08': [54, 34, 'price_d08'],
            'code_d09': [55, 34, 'price_d09'],
            'code_dm03': [39, 34, 'price_dm03'],
            'code_m00': [40, 34, 'price_m00'],
            'code_m01': [41, 34, 'price_m01'],
            'code_m02': [42, 34, 'price_m02'],
            'code_m03': [43, 34, 'price_m03'],
            'code_m04': [44, 34, 'price_m04'],
            'code_m05': [45, 34, 'price_m05'],
            'code_m06': [46, 34, 'price_m06'],
            'code_m07': [47, 34, 'price_m07'],
            'code_us': [48, 3, 'precio_us'],
            'code_dol1': [49, 3, 'dol_01'],
            'code_dol2': [50, 3, 'dol_02']
        }

        for price in self:
            if len(price.lines_ids) > 10000:
                raise UserError(_(
                    'For better performance you cannot import more than 10,000 lines at once, verify please...'))

            for line in price.lines_ids.filtered(
                    lambda lin: lin.state == 'draft'):
                # Producto existe con clave dada y es válido?
                # Busca producto de la linea del BoM original -OK

                self._cr.execute(
                    """SELECT id
                    FROM product_product
                    WHERE default_code = %s
                    AND active = True""", ([line.code_product]))
                # Si no existe registra mensaje de error
                if self._cr.rowcount:
                    pproduct = self._cr.fetchall()
                    item_id = pproduct[0]
                else:
                    message_body = "<b>%s:</b>" % (
                        "Product not found: " + line.code_product)
                    price.message_post(body=message_body)
                    continue

                tovalidate = (
                    line.price_mex, line.price_d00, line.price_d00_01,
                    line.price_d01, line.price_d02, line.price_d03,
                    line.price_d04, line.price_d05, line.price_d06,
                    line.price_d07, line.price_d08, line.price_d09,
                    line.price_dm03, line.price_m00, line.price_m01,
                    line.price_m02, line.price_m03, line.price_m04,
                    line.price_m05, line.price_m06, line.price_m07,
                    line.precio_us, line.dol_01, line.dol_01)
                if any(elem <= 0 for elem in tovalidate):
                    message_body_line = "<b>%s:</b>" % (
                        "Invalid price in one row for product: " + line.code_product)
                    price.message_post(body=message_body_line)
                    continue

                query = """
                    INSERT INTO product_pricelist_item(product_id,pricelist_id,
                    fixed_price,min_quantity,applied_on,base,currency_id,
                    company_id,compute_price,create_date,write_date,create_uid,
                    write_uid)
                    VALUES(%s,%s,%s,%s,'1_product','list_price',%s,%s,
                        'fixed',now(),now(),%s,%s)
                    ON CONFLICT (company_id,currency_id,product_id,
                        pricelist_id,min_quantity,applied_on)
                    DO UPDATE SET fixed_price = %s, write_uid = %s,
                        write_date = NOW();
                    """

                for pr_list in pricelist:
                    self._cr.execute(query, (
                        item_id, pricelist[pr_list][0],
                        line[pricelist[pr_list][2]], price.min_qty,
                        pricelist[pr_list][1], self.env.user.company_id.id,
                        self.env.user.id, self.env.user.id,
                        line[pricelist[pr_list][2]], self.env.user.id))

                self._cr.execute("""
                    UPDATE product_pricelist_import_line SET state = 'done',
                    write_uid = %s, write_date = NOW(), datedone = NOW()
                    WHERE id = %s""", (self.env.user.id,
                                       line.id))
                self.env.cr.commit()

            price.state = 'done'


class ProductPricelistImportLine(models.Model):
    _name = 'product.pricelist.import.line'
    _description = 'Product Pricelist Import Line'

    product_pricelist_import_id = fields.Many2one(
        'product.pricelist.import',
        string='Product Pricelist Import',
        ondelete='cascade',
        index=2,
        required=True,
    )

    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done')],
        string='State',
        default='draft',
    )

    datedone = fields.Datetime(
        string='Date done',
    )

    code_product = fields.Char(
        string='Code Master',
        required=True,
    )

    price_mex = fields.Float(
        string='Price Mex',
        required=True,
    )

    price_d00 = fields.Float(
        string='D00',
        required=True,
    )

    price_d00_01 = fields.Float(
        string='D00-01',
        required=True,
    )

    price_d01 = fields.Float(
        string='D01',
        required=True,
    )

    price_d02 = fields.Float(
        string='D02',
        required=True,
    )

    price_d03 = fields.Float(
        string='D03',
        required=True,
    )

    price_d04 = fields.Float(
        string='D04',
        required=True,
    )

    price_d05 = fields.Float(
        string='D05',
        required=True,
    )

    price_d06 = fields.Float(
        string='D06',
        required=True,
    )

    price_d07 = fields.Float(
        string='D07',
        required=True,
    )

    price_d08 = fields.Float(
        string='D08',
        required=True,
    )

    price_d09 = fields.Float(
        string='D09',
        required=True,
    )

    price_dm03 = fields.Float(
        string='DM03',
        required=True,
    )

    price_m00 = fields.Float(
        string='M00',
        required=True,
    )

    price_m01 = fields.Float(
        string='M01',
        required=True,
    )

    price_m02 = fields.Float(
        string='M02',
        required=True,
    )

    price_m03 = fields.Float(
        string='M03',
        required=True,
    )

    price_m04 = fields.Float(
        string='M04',
        required=True,
    )

    price_m05 = fields.Float(
        string='M05',
        required=True,
    )

    price_m06 = fields.Float(
        string='M06',
        required=True,
    )

    price_m07 = fields.Float(
        string='M07',
        required=True,
    )

    precio_us = fields.Float(
        string='Price US',
        required=True,
    )

    dol_01 = fields.Float(
        string='DOL01',
        required=True,
    )

    dol_02 = fields.Float(
        string='DOL02',
        required=True,
    )
