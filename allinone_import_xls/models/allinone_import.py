# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

#import cStringIO
import base64
import time
import xlwt
import xlrd
import decimal

from . import style_format
from io import StringIO, BytesIO
from datetime import datetime
from operator import itemgetter
from itertools import groupby
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, pycompat
import odoo.addons.decimal_precision as dp


MAPPING_DICT = {
                'Barcode':'barcode',
                'Qty':'product_qty',
                'Ref': 'ref',
                'Unit Price': 'price_unit',
                'Schedule Date': 'date_planned'
                }


class allinoneImportLines(models.Model):
    _name = 'allinone.import.lines'
    _description = 'allinone Import Lines'
    _order = 'valid'

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            price = price_total = 0.0
            if line.line_id.purchase:
                taxes = line.taxes_id.compute_all(line.price_unit, line.line_id.purchase_currency_id, line.product_qty, product=line.product_id, partner=line.line_id.supplier_id)
                price = taxes['total_excluded']
                price_total = taxes['total_included']
            elif line.line_id.sales:
                taxes = line.taxes_id.compute_all(line.price_unit, line.line_id.sales_pricelist_id.currency_id, line.product_qty, product=line.product_id, partner=line.line_id.customer_id)
                price = taxes['total_excluded']
                price_total = taxes['total_included']
            line.update({
                'price_subtotal': price,
                'price_total': price_total,
                'price_tax': price_total - price
            })

    barcode = fields.Char('Barcode')
    product_id = fields.Many2one('product.product', 'Product')
    product_qty = fields.Float('Quantity')
    price_unit = fields.Float('Unit Price')
    taxes_id = fields.Many2many('account.tax',
                                'mixed_import_taxe',
                                'line_id',
                                'tax_id', 'Taxes')
    price_subtotal = fields.Float(
          compute='_compute_amount',
          string='Subtotal', digits=dp.get_precision('Account'))
    price_total = fields.Float(
          compute='_compute_amount',
          string='Total',
          readonly=True,
          store=True)
    price_tax = fields.Float(
          compute='_compute_amount',
          string='Tax',
          store=True)

    valid = fields.Boolean('Valid?')
    ref = fields.Char('Reference')
    date_planned = fields.Date('Date Planned')
    #partner_ref = fields.Char('Reference')
    line_id = fields.Many2one('allinone.import', 'Lines')


class allinoneQuotation(models.Model):
    _name = 'allinone.import'
    _description = 'Import Data'

    @api.depends('allinone_lines.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            # dont calculate if order not to be purchase.
            if not order.purchase:
                order.update({
                    'pur_amount_untaxed': 0.0,
                    'pur_amount_tax': 0.0,
                    'pur_amount_total': 0.0,
                })
            else:
                for line in order.allinone_lines:
                    if line.valid:
                        amount_untaxed += line.price_subtotal
                    else:
                        amount_untaxed += 0.0
                    # FORWARDPORT UP TO 10.0
                    if order.company_id.tax_calculation_rounding_method == 'round_globally':
                        taxes = line.taxes_id.compute_all(line.price_unit,
                                                          line.line_id.currency_id,
                                                          line.product_qty,
                                                          product=line.product_id,
                                                          partner=line.line_id.partner_id)
                        amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                    else:
                        amount_tax += line.price_tax
                order.update({
                    'pur_amount_untaxed': order.purchase_currency_id.round(amount_untaxed),
                    'pur_amount_tax': order.purchase_currency_id.round(amount_tax),
                    'pur_amount_total': amount_untaxed + amount_tax,
                })

    @api.depends('allinone_lines.price_total')
    def _s_amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            if not order.sales:
                order.update({
                        'sales_amount_untaxed': 0.0,
                        'sales_amount_tax': 0.0,
                        'sales_amount_total': 0.0,
                })
            else:
                for line in order.allinone_lines:
                    amount_untaxed += line.price_subtotal
                    # FORWARDPORT UP TO 10.0
                    if order.company_id.tax_calculation_rounding_method == 'round_globally':
                        price = line.price_unit
                        taxes = line.taxes_id.compute_all(price, line.line_id.sales_pricelist_id.currency_id, line.product_qty, product=line.product_id, partner=line.line_id.partner_id)
                        amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                    else:
                        amount_tax += line.price_tax
                order.update({
                    'sales_amount_untaxed': order.sales_pricelist_id.currency_id.round(amount_untaxed),
                    'sales_amount_tax': order.sales_pricelist_id.currency_id.round(amount_tax),
                    'sales_amount_total': amount_untaxed + amount_tax,
                })

    def _get_picking_in(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id', '=', False)])
            if not types:
                raise Warning(_("Make sure you have at least an incoming picking type defined"))
        return types and types[0].id or False

    name = fields.Char(string='Number')
    note = fields.Text(string='Notes')
    quotation_csv = fields.Binary(string='Select File(.xls)', filters='*.xls')
    allinone_lines = fields.One2many('allinone.import.lines',
                                    'line_id',
                                    string='Lines')
    f_name = fields.Char(string='Filename')
    import_date = fields.Datetime(
      string='Import Date',
      readonly=True, states={'draft':[('readonly', False)]},
      default=lambda self: fields.Datetime.now())
    state = fields.Selection([
                               ('draft', 'Draft'),
                               ('in_purchase', 'In-Purchase Mode'),
                               ('purchased', 'Purchase(Imported)'),
                               ('in_sales', 'In-Sales Mode'),
                               ('sold', 'Sales(Imported)'),
                               ('in_internal_transfer', 'In-Internal Transfer Mode'),
                               ('internal_transfered', 'Transfered(Imported)'),
                               ('in_reco', 'In-Reconciliation Mode'),
                               ('reconciled', 'Reconcile(Imported)')], 'Status',
                             readonly=True,
                             copy=False,
                             default='draft')

    purchase = fields.Boolean('Purchase?')
    sales = fields.Boolean('Sales?')
    transfer = fields.Boolean('Internal Transfer?')
    reco = fields.Boolean('Reconciliation?')
    confirm_process = fields.Boolean('Confirm Process')
    process_completed = fields.Boolean('Process Completed')
    group_entries = fields.Boolean('Group entries?', help="True, It will auto merge products with group by.")
    base_on = fields.Selection([
                               ('default_code', 'Product Internal Reference'),
                               ('ean13', 'Product EAN13')
                               ], 'Base On', copy=False,
                               default='default_code')
    notimport_xls = fields.Binary('Not Found Product XLS', readonly=True)
    fname_notimport = fields.Char('Not Found Product')
    # Generic Fields
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id.id)
    company_currency = fields.Many2one(related='company_id.currency_id', string='Currency', readonly=True)

    # Purchase fields
    supplier_id = fields.Many2one('res.partner', 'Supplier', domain=[('supplier', '=', True)])
    purchase_currency_id = fields.Many2one('res.currency', string='Purchase Currency')
    # purchase_pricelist_id = fields.Many2one(related='supplier_id.property_product_pricelist_purchase', string='Purchase Pricelist')
    picking_type_id = fields.Many2one(
          'stock.picking.type',
          string='Deliver To',
          help="This will determine picking type of incoming shipment",
          default=_get_picking_in)

    pur_amount_untaxed = fields.Float(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all')
    pur_amount_tax = fields.Float(string='Taxes', store=True, readonly=True, compute='_amount_all')
    pur_amount_total = fields.Float(string='Total', store=True, readonly=True, compute='_amount_all')
    purchase_id = fields.Many2one('purchase.order', string='Purchase Quotation', readonly=True)
    purchase_ids = fields.Many2many('purchase.order', string='Purchase Quotations', readonly=True)

    # Sales fields
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)])
    sales_pricelist_id = fields.Many2one(related='customer_id.property_product_pricelist', string='Sales Pricelist')
    sales_currency_id = fields.Many2one('res.currency', string='Currency')
    sales_amount_untaxed = fields.Float(string='Untaxed Amount', store=True, readonly=True, compute='_s_amount_all')
    sales_amount_tax = fields.Float(string='Taxes', store=True, readonly=True, compute='_s_amount_all')
    sales_amount_total = fields.Float(string='Total', store=True, readonly=True, compute='_s_amount_all')
    sales_warehouse_id = fields.Many2one('stock.warehouse', string='Sales From Warehouse')
    sale_id = fields.Many2one('sale.order', string='Sales Quotation', readonly=True)
    sale_ids = fields.Many2many('sale.order', string='Sales Quotation', readonly=True)

    # Transfer fields
    location_id = fields.Many2one('stock.location', string='Source Location')
    location_dest_id = fields.Many2one('stock.location', string='Destination Location')
    picking_id = fields.Many2one('stock.picking', string='Internal Picking', readonly=True)

    # Reconcilation fields
    reco_location_id = fields.Many2one('stock.location', string='Reco Location')
    reco_id = fields.Many2one('stock.inventory', string='Reconciliation Order', readonly=True)

    @api.onchange('location_id', 'location_dest_id')
    def onchange_location_id(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id

        domain = []
        if self.location_id.usage == 'internal':
            domain.append(
                ('warehouse_id', '=', self.location_id.stock_warehouse_id.id))
        elif self.location_dest_id.usage == 'internal':
            domain.append(
                ('warehouse_id', '=', self.location_dest_id.stock_warehouse_id.id))
        else:
            domain.append(('warehouse_id.company_id', '=', company_id))

        if self.location_id.usage == 'inventory' and self.location_dest_id.usage == 'internal':
            domain.append(('code', '=', 'incoming'))
        elif self.location_id.usage == 'internal' and self.location_dest_id.usage == 'inventory':
            domain.append(('code', '=', 'outgoing'))
        else:
            domain.append(('code', '=', 'internal'))

        types = type_obj.search(domain)

        # types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search([('code', '=', 'internal'), ('warehouse_id', '=', False)])
            if not types:
                raise Warning(_("Make sure you have at least an incoming picking type defined"))

        self.picking_type_id = types and types[0].id or False
        # return types and types[0].id or False

    @api.onchange('supplier_id', 'company_id')
    def onchange_partner_id(self):
        purchase_currency = False
        if self.supplier_id:
            purchase_currency = self.supplier_id.property_purchase_currency_id.id or self.env.user.company_id.currency_id.id
        self.purchase_currency_id = purchase_currency

    @api.onchange('customer_id', 'company_id')
    def onchange_customer_id(self):
        sales_currency_id = False
        if self.customer_id:
            sales_currency_id = self.customer_id.property_product_pricelist and self.customer_id.property_product_pricelist.currency_id.id or self.env.user.company_id.currency_id.id
        self.sales_currency_id = sales_currency_id

    @api.multi
    def group_products(self):
        """
        Group Entries
            Product A : 1 Qty
            Product A : 1 Qty
            Product A : 1 Qty
            Product B : 2 Qty
            Product c : 1 Qty
            Product c : 1 Qty
        Output will be
            Product A : 3 Qty
            Product B : 2 Qty
            Product c : 2 Qty
        """
        scanlines_obj = self.env['allinone.import.lines']
        current = self

        if not current.allinone_lines:
            raise Warning(_('Without lines we cannot apply any group mechanizam.'))

        self._cr.execute("""
                        SELECT sil.product_id AS product_id,sum(sil.product_qty) AS qty from allinone_import_lines sil, allinone_import si
                        WHERE  sil.line_id = si.id AND si.id = %s
                        GROUP BY sil.product_id
                """ % (self.id))
        values = self._cr.dictfetchall()

        for args in values:
            line_ids = scanlines_obj.search([('product_id', '=', args['product_id']), ('line_id', '=', self.id)])
            total_line_ids = list(set([x.id for x in line_ids]))
            if line_ids:
                line_ids[0].write({
                                'product_qty': args.get('qty', 1.0) or 1.0
                                })
                total_line_ids.remove(line_ids[0].id)
                if total_line_ids:
                    scanlines_obj.browse(total_line_ids).unlink()

    @api.multi
    def action_purchase(self):
        self.ensure_one()
        context = dict(self._context or {})
        context.update({
                        'action': 'purchase'
                        })
        return {
            'name': _('Purchase Entries'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'allinone.message',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }

    @api.multi
    def action_sales(self):
        self.ensure_one()
        context = dict(self._context or {})
        context.update({
                        'action': 'sales'
                        })
        return {
            'name': _('Sales Entries'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'allinone.message',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }

    @api.multi
    def action_transfer(self):
        self.ensure_one()
        context = dict(self._context or {})
        context.update({
                        'action': 'transfer'
                        })
        return {
            'name': _('Transfer Entries'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'allinone.message',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }

    @api.multi
    def action_reco(self):
        self.ensure_one()
        context = dict(self._context or {})
        context.update({
                        'action': 'reco'
                        })
        return {
            'name': _('Reco Entries'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'allinone.message',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }

    @api.multi
    def action_validate(self):
        """
        Confirmed which action will be performed.
        """
        self.ensure_one()
        pair = {
                'purchase': 'in_purchase',
                'sales': 'in_sales',
                'transfer': 'in_internal_transfer',
                'reco': 'in_reco'
                }

        self.write({
             self._context.get('action', 'purchase'): True,
             'confirm_process': True,
             'state': pair[self._context.get('action', 'purchase')],
             'name': self.env['ir.sequence'].next_by_code('allinone.import') or '/'
             })

    @api.onchange('purchase', 'sales', 'transfer', 'reco')
    def onchange_common(self):
        """
        - Just put some attrs base on confirm_process button.
        """
        res = {
               'value': {
                          'confirm_process': False
                          }
               }
        if self.purchase or self.sales or self.transfer or self.reco:
            res['value']['confirm_process'] = True
        return res

    @api.model
    def xls_exportdata(self, notfound_import):
        wb1 = xlwt.Workbook()
        ws1 = wb1.add_sheet('Product Not Found')

        para_style = style_format.font_style(position='center', bold=1, fontos='black', font_height=150)
        para_style_in = style_format.font_style(position='center', fontos='black', font_height=150)

        # Headers
        ws1.write_merge(0, 0, 0, 0, 'Barcode ', para_style)
        ws1.write_merge(0, 0, 1, 1, 'Qty', para_style)

        raw_start = raw_end = 0
        for prod in notfound_import:
            raw_start += 1
            raw_end += 1
            ws1.write_merge(raw_start, raw_end, 0, 0, prod[0], para_style_in)
            ws1.write_merge(raw_start, raw_end, 1, 1, prod[1], para_style_in)

        wb1.save('/tmp/notfound_export.xls')
        result_file = open('/tmp/notfound_export.xls', 'rb').read()
        return result_file

    @api.model
    def _get_display_price(self, product, spricelist):
        if spricelist.discount_policy == 'without_discount':
            from_currency = self.env.user.company_id.currency_id
            return from_currency.compute(product.lst_price, spricelist.currency_id)
        return product.with_context(pricelist=spricelist.id).price

    @api.model
    def _converted_date(self, to_date):
        return to_date

    @api.model
    def _converted_barcode_value(self, barcode_value):
        if isinstance(barcode_value, (float, int)):
            barcode_value = str(decimal.Decimal(barcode_value))
        # barcode_value = barcode_value and barcode_value.split(".")[0] or ''
        barcode_value = barcode_value.replace("'", "")
        return barcode_value

    @api.model
    def _get_check_value(self, book, cell):
        exact_value = cell.value
        if cell.ctype is xlrd.XL_CELL_NUMBER:
            is_float = cell.value % 1 != 0.0
            if is_float:
                exact_value = pycompat.text_type(cell.value)
            else:
                exact_value = pycompat.text_type(int(cell.value))
#         elif cell.ctype is xlrd.XL_CELL_DATE:
#             is_datetime = cell.value % 1 != 0.0
#             # emulate xldate_as_datetime for pre-0.9.3
#             dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(cell.value, book.datemode))
#             if is_datetime:
#                 exact_value = dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
#             else:
#                 exact_value = dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
        elif cell.ctype is xlrd.XL_CELL_BOOLEAN:
            exact_value = u'True' if cell.value else u'False'
        elif cell.ctype is xlrd.XL_CELL_ERROR:
            raise ValueError(
                _("Error cell found while reading XLS/XLSX file: %s") % 
                xlrd.error_text_from_code.get(
                    cell.value, "unknown error code %s" % cell.value)
            )
        return exact_value

    @api.multi
    def compare_lines(self):
        """
            Read XLS data and create Pre-Product lines.
        """
        self.ensure_one()
        pro_obj = self.env['product.product']
        sil = self.env['allinone.import.lines']
        current_rec = self
        xls_rec = current_rec.quotation_csv
        if not xls_rec:
            raise Warning(_('There is no file !'))

        # Read xls file
        #string_data = StringIO(base64.decodestring(xls_rec).decode())
        #string_data = cStringIO.StringIO(base64.decodestring(xls_rec))
        xls_file = xlrd.open_workbook(file_contents=base64.decodestring(self.quotation_csv))
        sheet = xls_file.sheet_by_index(0)

        # Mapping Header
        header_list = []
        try:
            header = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols)]
        except:
            raise Warning(_('You can only upload .XLS file Extension.'))

        for mapping in header:
            try:
                if (mapping.lower()).strip() in ('barcode', 'barcode:'):
                    mapping = 'Barcode'
                if (mapping.lower()).strip() in ('quantity', 'qty', 'quantity:', 'qty:'):
                    mapping = 'Qty'
                if (mapping.lower()).strip() in ('unit price', ' unit price', 'price'):
                    mapping = 'Unit Price'
                if (mapping.lower()).strip() in ('reference', ' Reference', 'ref'):
                    mapping = 'Ref'
                if (mapping.lower()).strip() in ('schedule date', ' schedule date', 'date'):
                    mapping = 'Schedule Date'
                header_list.append(MAPPING_DICT[mapping.strip()])
            except:
                raise Warning(_('Column not found (%s)' % (mapping)))

        if not header_list:
            raise Warning(_('Please check your file'))

        # mapping header with row
        row_list = []
        for row_index in xrange(1, sheet.nrows):
            row_list.append({
                 header_list[col_index]:
                 self._get_check_value(sheet, sheet.cell(row_index, col_index))
                 for col_index in xrange(sheet.ncols)
                 })

        string = ''
        count = 0
        self = self.with_context(base_on=current_rec.base_on)
        notfound_import = []
        final_list_to_import = []
        for row_dict in row_list:
            count += 1
            product_id = self._find_product_id(row_dict)
            barcode = self._converted_barcode_value(row_dict.get('barcode'))
            if product_id:
                row_dict.update({
                                 'product_id':product_id,
                                 'barcode': barcode
                                 })
                final_list_to_import.append(row_dict)
            else:
                notfound_import.append((barcode, row_dict.get('product_qty', '')))
                string += 'Line number(' + str(count) + '), Barcode(' + barcode + ').\n' 

        for import_line in final_list_to_import:
            if not import_line.get('product_qty'):
                import_line.update(product_qty=1.0)
            pro = pro_obj.browse(import_line['product_id'])
            price = import_line.get('price_unit', 0.0) or 0.0
            reference = import_line.get('ref', '') or ''

            date_planned = import_line.get('date_planned', False) or False
            if date_planned:
                converted_date = datetime(*xlrd.xldate_as_tuple(date_planned,
                                                                xls_file.datemode
                                                                ))
                date_planned = converted_date.strftime(DEFAULT_SERVER_DATE_FORMAT)

            #date_planned = import_line.get('date_planned', False) or False
            if current_rec.purchase:
                taxes = [(6, 0, [x.id for x in pro.supplier_taxes_id])]
            elif current_rec.sales:
                taxes = [(6, 0, [x.id for x in pro.taxes_id])]
            else:
                taxes = []
            import_line.update(
                               product_id=pro.id,
                               valid=True,
                               taxes_id=taxes,
                               price_unit=price,
                               reference=reference,
                               date_planned=date_planned,
                               line_id=self.id
                               )

        # Import data into lines
        self._cr.execute(""" DELETE FROM allinone_import_lines WHERE line_id = %s """ % (self.id))
        for imprt in final_list_to_import:
            sil.create(imprt)
            sil.update({
                        'date_planned': self._converted_date(sil.date_planned)
                        })
        self.write({
                  'notimport_xls':base64.encodestring(self.xls_exportdata(notfound_import)),
                  'fname_notimport' : "notfoundproducts.xls"
                  })
        return True

    @api.model
    def _get_eannumber(self, eanvalue):
        if not eanvalue: return ''
        try:
            ean13 = str(int(eanvalue))
        except:
            raise Warning(_(""" EAN base process, you must put a numeric values in xls sheet."""))
        if ean13 and len(ean13) == 10:
            ean13 = '000' + str(ean13)
        elif ean13 and len(ean13) == 11:
            ean13 = '00' + str(ean13)
        elif ean13 and len(ean13) == 12:
            ean13 = '0' + str(ean13)
        elif ean13 and len(ean13) == 14:
            ean13 = ean13[1:]
        return ean13

    @api.model
    def _find_product_id(self, line):
        prod_obj = self.env['product.product']
        search_args = self._converted_barcode_value(line['barcode'])
        base_on = self._context and self._context.get('base_on', 'default_code') or 'default_code'
        base_on_field = 'default_code'
        if base_on == 'ean13':
            base_on_field = 'barcode'
            search_args = self._get_eannumber(search_args)
        product_ids = prod_obj.search([(base_on_field, '=', search_args)])
        if (not product_ids) and line['barcode']:
            product_ids = prod_obj.search([(base_on_field, '=', search_args + ' ')])
        return product_ids and product_ids[0].id or False

    @api.multi
    def action_create_po(self):
        """
        - Create Purchase Order
        """
        self.ensure_one()
        pur_obj = self.env['purchase.order']
        purline_obj = self.env['purchase.order.line']
        current = self
        if not current.allinone_lines:
            raise Warning(_('Atleast one line to create purchase order.'))
        valid = [x.valid for x in current.allinone_lines] 
        if not any(valid):
            raise Warning(_('Atleast one valid line to create purchase order.'))

        all_validlines = [{'line_id':y, 'ref':y.ref} for y in current.allinone_lines if y.valid]

        sort_by_lines = sorted(all_validlines, key=itemgetter('ref'))
        group_by_lines = dict((k, [v for v in itr]) for k, itr in groupby(sort_by_lines, itemgetter('ref')))

        total_order_generated = ''
        count = 0
        total_purchase_ids = []
        for key, value in group_by_lines.items():
            count += 1
            purchase_rec = pur_obj.create(self._create_purchase_vals(current, key))
            total_purchase_ids.append(purchase_rec.id)
            total_order_generated += str(count) + ')Purchase Quotation : ' + str(purchase_rec.name) + '\n'
            for get_rec in value:
                purline_obj.create(self._purchase_lines(get_rec['line_id'], purchase_rec.id))

        self.write({
                 'purchase_id': purchase_rec.id,
                 'purchase_ids': [(6, 0, total_purchase_ids)],
                 'state': 'purchased',
                 'process_completed': True,
                 'note': total_order_generated
                 })
        return True

    @api.model
    def _create_purchase_vals(self, current, ref=''):
        partner = current.supplier_id
        return {
                'name': self.env['ir.sequence'].next_by_code('purchase.order'),
                'partner_id': partner.id,
                'currency_id': current.purchase_currency_id and current.purchase_currency_id.id or False,
                'date_order': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'fiscal_position': self.env['account.fiscal.position'].with_context(company_id=current.company_id.id).get_fiscal_position(partner.id),
                'payment_term_id': partner.property_supplier_payment_term_id.id or False,
                'picking_type_id': current.picking_type_id.id,
                'company_id': self.env.user.company_id.id,
                'location_id': current.picking_type_id.default_location_dest_id.id,
                'partner_ref': ref
                }

    @api.model
    def _purchase_lines(self, line, purchase_id):
        return {
                'name': line.product_id.name,
                'product_qty': line.product_qty,
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_po_id.id,
                'price_unit': line.price_unit or 0.0,
                'date_planned': line.date_planned or time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                #'date_planned': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'taxes_id': [(6, 0, [x.id for x in line.product_id.supplier_taxes_id])],
                'order_id': purchase_id
                }

    @api.model
    def _create_sales_vals(self, current, key=''):
        partner = current.customer_id
        return {
                'name': self.env['ir.sequence'].next_by_code('sale.order'),
                'partner_id': partner.id,
                'pricelist_id': current.sales_pricelist_id.id,
                'currency_id': current.sales_pricelist_id and current.sales_pricelist_id.currency_id.id or False,
                'date_order': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'warehouse_id': current.sales_warehouse_id.id,
                'company_id': self.env.user.company_id.id,
                'picking_policy':'direct',
                'order_policy':'manual',
                'client_order_ref': key
                }

    @api.model
    def _sale_lines(self, line, sale_id):
        return {
                'name': line.product_id.name,
                'product_uom_qty': line.product_qty,
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_id.id,
                'product_uos_qty':line.product_qty,
                'price_unit': line.price_unit or 0.0,
                'date_planned': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'tax_id': [(6, 0, [x.id for x in line.taxes_id])],
                'order_id': sale_id
                }

    @api.multi
    def action_create_so(self):
        """
        - Create Purchase Order
        """
        self.ensure_one()
        sale_obj = self.env['sale.order']
        saleline_obj = self.env['sale.order.line']
        current = self
        if not current.allinone_lines:
            raise Warning(_('Atleast one line to create sales order.'))
        valid = [x.valid for x in current.allinone_lines] 
        if not any(valid):
            raise Warning(_('Atleast one valid line to create sales order.'))

        all_validlines = [{'line_id':y, 'ref':y.ref} for y in current.allinone_lines if y.valid]

        sort_by_lines = sorted(all_validlines, key=itemgetter('ref'))
        group_by_lines = dict((k, [v for v in itr]) for k, itr in groupby(sort_by_lines, itemgetter('ref')))

        total_order_generated = ''
        count = 0
        total_sale_ids = []
        for key, value in group_by_lines.items():
            count += 1
            sale_id = sale_obj.create(self._create_sales_vals(current, key))
            sale_rec = sale_id
            total_sale_ids.append(sale_rec.id)
            total_order_generated += str(count) + ')Sales Quotation : ' + str(sale_rec.name) + '\n'
            for get_rec in value:
                saleline_obj.create(self._sale_lines(get_rec['line_id'], sale_id.id))

        self.write({
                     'sale_id': sale_id.id,
                     'sale_ids' : [(6,0, total_sale_ids)],
                     'state':'sold',
                     'process_completed':True,
                     'note': total_order_generated
                     })
        return True

    @api.model
    def _get_picking_internal(self, location_id):
        """
        Find internal type from source location
        """
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id

        domain = []
        if self.location_id.usage == 'internal':
            domain.append(
                ('warehouse_id', '=', self.location_id.stock_warehouse_id.id))
        elif self.location_dest_id.usage == 'internal':
            domain.append(
                ('warehouse_id', '=', self.location_dest_id.stock_warehouse_id.id))
        else:
            domain.append(('warehouse_id.company_id', '=', company_id))

        if self.location_id.usage == 'inventory' and self.location_dest_id.usage == 'internal':
            domain.append(('code', '=', 'incoming'))
        elif self.location_id.usage == 'internal' and self.location_dest_id.usage == 'inventory':
            domain.append(('code', '=', 'outgoing'))
        else:
            domain.append(('code', '=', 'internal'))

        types = type_obj.search(domain)

        # types = type_obj.search([('code', '=', 'internal'), ('warehouse_id.company_id', '=', company_id)])

        if not types:
            types = type_obj.search([('code', '=', 'internal'), ('warehouse_id', '=', False)])
            if not types:
                raise Warning(_("Make sure you have at least an internal picking type defined.\n for that you have to activate 'Advanced routing of products using rules' from inventory setting."))
        return types and types[0] or False

    @api.model
    def _create_pick_vals(self, current):
        internal_type = self._get_picking_internal(current.location_id.id)
        return {
                'origin': current.name,
                'company_id': current.company_id and current.company_id.id or False,
                'picking_type_id': internal_type.id,
                'location_dest_id': current.location_dest_id and current.location_dest_id.id or internal_type.default_location_src_id,
                'location_id': current.location_id and current.location_id.id or internal_type.default_location_src_id,
                'note': current.note,
                }

    @api.model
    def _move_lines(self, current, line, pick_id):
        return {
                'name': (line.line_id.name or '') + ':' + current.location_id.name + '>' + current.location_dest_id.name,
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_id.id,
                'product_uom_qty': line.product_qty,
                'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'company_id': line.line_id.company_id.id,
                'state': 'draft',
                'location_id': current.location_id.id,
                'location_dest_id': current.location_dest_id.id,
                'picking_id': pick_id
                }

    @api.multi
    def action_create_int_transfer(self):
        """
        -Create Internal Transfer Picking
        """
        self.ensure_one()
        pick_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        current = self

        if not current.allinone_lines:
            raise Warning(_('Atleast one line to create Transfer Picking.'))
        valid = [x.valid for x in current.allinone_lines] 
        if not any(valid):
            raise Warning(_('Atleast one valid line to create Transfer Picking.'))

        pick_id = pick_obj.create(self._create_pick_vals(current))

        for line in current.allinone_lines:
            if line.valid and (line.product_id.type in ('product', 'consu')):
                move_obj.create(self._move_lines(current, line, pick_id.id))

        self.write({
                 'picking_id': pick_id.id,
                 'state':'internal_transfered',
                 'process_completed':True
                 })

        return True

    @api.model
    def _create_reco_vals(self, current):
        return {
                'name': current.name,
                'company_id': current.company_id and current.company_id.id or False,
                'location_id': current.reco_location_id.id
                }

    @api.model
    def _inventoy_lines(self, line, inv_id, reco_location_id):
        line_id = False
        invline_obj = self.env['stock.inventory.line']
        line_ids = invline_obj.search([('inventory_id', '=', inv_id), ('product_id', '=', line.product_id.id)])
        if line_ids:
            line_ids.write({'product_qty': line.product_qty})
        else:
            line_id = invline_obj.create({
                                        'product_id':line.product_id.id,
                                        'product_qty':line.product_qty,
                                        'inventory_id': inv_id,
                                        'location_id': reco_location_id,
                                        'product_uom_id': line.product_id.uom_id.id,
                                        'theoretical_qty':0.0
                                        })
        return (line_ids and line_ids[0].id) or (line_id and line_id.id) or False

    @api.model
    def _remove_line_ids(self, valid_line_ids, total_line_ids):
        remove_list = []
        for remove_el in total_line_ids:
            if remove_el not in valid_line_ids:
                remove_list.append(remove_el)
        if remove_list:
            self._cr.execute('DELETE  from stock_inventory_line where id IN %s', (tuple(remove_list),))
        return True

    @api.multi
    def action_create_reco(self):
        """
        - Create Physical inventory
        """
        self.ensure_one()
        inv_obj = self.env['stock.inventory']
        invline_obj = self.env['stock.inventory.line']
        current = self

        if not current.allinone_lines:
            raise Warning(_('Atleast one line to create Reco Order.'))
        valid = [x.valid for x in current.allinone_lines] 
        if not any(valid):
            raise Warning(_('Atleast one valid line to create Reco Order.'))

        reco_id = inv_obj.create(self._create_reco_vals(current))
        reco_id.action_start()

        valid_line_ids = []
        inv_rec = reco_id
        for line in current.allinone_lines:
            if line.valid:
                valid_line_ids.append(self._inventoy_lines(line, reco_id.id, current.reco_location_id.id))

        total_line_ids = [x.id for x in inv_rec.line_ids]
        self._remove_line_ids(valid_line_ids, total_line_ids)

        self.write({
                 'reco_id': reco_id.id,
                 'state':'reconciled',
                 'process_completed':True
                 })

        return True

    @api.multi
    def button_dummy(self):
        return True

    @api.one
    def copy(self, default=None):
        raise Warning(_("""Please create new record instead of copy!!!"""))

    @api.multi
    def unlink(self):
        for order in self:
            if order.process_completed:
                raise Warning(_('Completed orders cannot be deleted.'))
        return super(allinoneQuotation, self).unlink()


class image_location_save(models.Model):
    _name = 'image.location.save'

    name = fields.Char('Number')
    image = fields.Binary('image')
