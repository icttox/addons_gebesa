# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    businness_partner_id = fields.Many2one(
        'res.partner',
        string='Business partner',
    )
    businness_partner_ids = fields.Many2many(
        'res.partner', string='Business partners',
        related='company_id.partner_ids'
    )
    has_businness_partner = fields.Boolean(
        string='Has a business partner',
        compute='_compute_has_businness_partner',
    )

    @api.depends('businness_partner_ids')
    def _compute_has_businness_partner(self):
        for purchase in self:
            if purchase.businness_partner_ids:
                purchase.has_businness_partner = True
            else:
                purchase.has_businness_partner = False

    @api.one
    def inter_company_create_sale_order(self, company):
        """ Create a Sale Order from the current PO (self)
            Note : In this method, reading the current PO is done as sudo, and the creation of the derived
            SO as intercompany_user, minimizing the access right required for the trigger user.
            :param company : the company of the created PO
            :rtype company : res.company record
        """
        if not self.env.user.has_group('multicompany_gebesa.allow_po_so_amount_discrepancy'):
            sale_order = self.env['sale.order'].sudo().search([
                ('name', '=', self.origin),
                ('company_id', '=', self.company_id.id)], limit=1)
            if sale_order:
                sale_order_lines = sale_order.order_line.filtered(lambda line: line.product_id.type == 'product')
                purchase_order_lines = self.order_line.filtered(lambda line: line.product_id.type == 'product')
                sale_lines_count = len(sale_order_lines)
                purchase_lines_count = len(purchase_order_lines)
                sale_lines_total = sum(sale_order_lines.mapped('product_uom_qty'))
                purchase_lines_total = sum(purchase_order_lines.mapped('product_qty'))
                if sale_lines_count != purchase_lines_count or sale_lines_total != purchase_lines_total:
                    raise ValidationError('La cantidad de líneas y la suma de cantidades no coincide entre la Orden de Compra y la Orden de Venta.')

        if self.company_id.country_id != self.env.ref('base.mx'):
            so = self.mapped('order_line').mapped('sale_line_id').mapped('order_id')
            if so and (not so.salesrep_id or not so.sales_person_id):
                raise ValidationError(
                    'No se ha extablecido el REP o el sales person en el pedido de venta')
        # self = self.with_context(force_company=company.id)
        sale_object = self.env['sale.order']
        company_partner = self.company_id.partner_id

        if self.businness_partner_id:
            company_partner = self.businness_partner_id

        # find user for creating and validation SO/PO from partner company
        intercompany_uid = company.intercompany_user_id and company.intercompany_user_id.id or False
        if not intercompany_uid:
            raise Warning(_('Provide at least one user for inter company relation for %s') % company.name)
        # check intercompany user acncess rights
        if not sale_object.sudo(intercompany_uid).check_access_rights('create', raise_exception=False):
            raise Warning(_("Inter company user of company %s doesn't have enough access rights") % company.name)

        # check pricelist currency should be same with SO/PO document
        if self.currency_id.id != company_partner.sudo(company.intercompany_user_id.id).property_product_pricelist.currency_id.id:
            raise Warning(_('You cannot create SO from PO because sale price list currency is different than purchase price list currency.'))

        # create the SO and generate its lines from the PO lines
        sale_line_object = self.env['sale.order.line']
        # read it as sudo, because inter-compagny user can not have the access right on PO
        sale_order_data = self.sudo()._prepare_sale_order_data(self.name, company_partner, company, self.dest_address_id and self.dest_address_id.id or False)
        sale_order = sale_object.sudo(intercompany_uid).create(sale_order_data[0])
        # lines are browse as sudo to access all data required to be copied on SO line (mainly for company dependent field like taxes)
        for line in self.order_line.sudo():
            so_line_vals = self.sudo(intercompany_uid)._prepare_sale_order_line_data(line, company, sale_order.id)
            sale_line_object.sudo(intercompany_uid).create(so_line_vals)

        # write vendor reference field on PO
        if not self.partner_ref:
            self.partner_ref = sale_order.name

        # Validation of sale order
        if company.auto_validation == 'validated':
            sale_order.sudo(intercompany_uid).action_confirm()

    @api.one
    def _prepare_sale_order_data(self, name, partner, company, direct_delivery_address):
        """ Generate the Sale Order values from the PO
            :param name : the origin client reference
            :rtype name : string
            :param partner : the partner reprenseting the company
            :rtype partner : res.partner record
            :param company : the company of the created SO
            :rtype company : res.company record
            :param direct_delivery_address : the address of the SO
            :rtype direct_delivery_address : res.partner record
        """
        partner_addr = partner.sudo().address_get(['invoice', 'delivery', 'contact'])
        if self.company_id.country_id.code != 'MX':
            shipping = False

            sale_id = self.order_line.mapped('sale_order_id')
            team_id = False
            if sale_id:
                sales_channel = sale_id.mapped('partner_id.team_id')
                if not sales_channel:
                    raise ValidationError('El cliente no tiene un canal de ventas asignado.')
                sales_channel_mpf = self.env['crm.team'].sudo().search([
                    ('name', '=', sales_channel.name),
                    ('company_id', '=', company.id)
                ], limit=1)
                if not sales_channel_mpf:
                    raise ValidationError('No existe el canal de ventas en MPF con el mismo nombre.')
                team_id = sales_channel_mpf
        else:
            default_shipping = self.env['res.partner'].sudo().search([
                ('parent_id', '=', partner.id),
                ('partner_type_id', '=', 2)], limit=1).id or False
            shipping = default_shipping or direct_delivery_address or partner_addr['delivery']
            team_id = partner.sudo(company.intercompany_user_id.id).team_id

        if self.businness_partner_id:
            shipping = self.env['res.partner'].sudo().search([
                ('parent_id', '=', partner.id),
                ('partner_type_id', '=', 2)], limit=1).id or False

        warehouse = company.warehouse_id and company.warehouse_id.company_id.id == company.id and company.warehouse_id or False
        if not warehouse:
            raise Warning(_('Configure correct warehouse for company(%s) from Menu: Settings/Users/Companies' % (company.name)))
        salesrep_id = self.mapped('order_line').mapped('sale_line_id').mapped(
            'order_id').mapped('salesrep_id')
        if salesrep_id:
            if salesrep_id[0].team_id:
                team_id = salesrep_id[0].team_id
            salesrep_id = salesrep_id[0].id
        else:
            salesrep_id = False
        sales_channel_id = team_id.id if team_id else False
        return {
            'name': self.env['ir.sequence'].sudo().next_by_code('sale.order') or '/',
            'company_id': company.id,
            'warehouse_id': warehouse.id,
            'client_order_ref': name,
            'partner_id': partner.id,
            'team_id': sales_channel_id,
            'pricelist_id': partner.sudo(company.intercompany_user_id.id).property_product_pricelist.id,
            'partner_invoice_id': partner_addr['invoice'],
            'date_order': self.date_order,
            'fiscal_position_id': partner.property_account_position_id.id,
            'user_id': False,
            'auto_generated': True,
            'auto_purchase_order_id': self.id,
            'notify_approval': partner.notify_approval,
            'partner_shipping_id': shipping,
            'salesrep_id': salesrep_id
        }

    @api.multi
    @api.onchange('businness_partner_id')
    def onchange_businness_partner_id(self):
        for purchase in self:
            for line in purchase.order_line:
                line._onchange_quantity()

    @api.model
    def _check_price_multicompany(self, line, company, sale_id):
        product = line.product_id.sudo(company.intercompany_user_id)
        so = self.env["sale.order"].sudo(company.intercompany_user_id).browse(sale_id)
        product_context = dict(self.env.context, partner_id=so.partner_id.id, date=so.date_order, uom=product.product_uom.id)
        final_price, rule_id = so.pricelist_id.with_context(product_context).get_product_price_rule(product, line.product_uom_qty or 1.0, so.partner_id)
        if rule_id:
            rule_id = self.env["product.pricelist.item"].sudo(company.intercompany_user_id).browse(rule_id)
            if (rule_id.product_id.id is not False or rule_id.product_tmpl_id.id is not False) and final_price != line.price_unit:
                raise Warning(_('The price of the product %s($%s) does not match that of the price list($%s)') % (line.product_id.default_code, line.price_unit, final_price))

        return True

    @api.model
    def _prepare_sale_order_line_data(self, line, company, sale_id):
        """ Generate the Sale Order Line values from the PO line
            :param line : the origin Purchase Order Line
            :rtype line : purchase.order.line record
            :param company : the company of the created SO
            :rtype company : res.company record
            :param sale_id : the id of the SO
        """
        # it may not affected because of parallel company relation
        if self.company_id.country_id.fiscal_code == 'MEX':
            self._check_price_multicompany(line, company, sale_id)
        route_obj = self.env['stock.location.route']
        price = line.price_unit or 0.0
        taxes = line.taxes_id
        lang = line.order_id.company_id.partner_id.lang
        if line.product_id:
            taxes = line.product_id.taxes_id
            if not line.product_id.family_id:
                raise Warning(_('Product %s has no family assigned') % line.product_id.default_code)
            route_id = route_obj.search([(
                'family_ids', '=', line.product_id.family_id.id)])
            if len(route_id) < 1:
                raise Warning(_('Family %s has not assigned a production route') % line.product_id.family_id.name)
            if len(route_id) > 1:
                raise Warning(_('Family %s has more than one production route assigned') % line.product_id.family_id.name)
            route_id = route_id.id
        company_taxes = [tax_rec for tax_rec in taxes if tax_rec.company_id.id == company.id]
        if sale_id:
            so = self.env["sale.order"].sudo(company.intercompany_user_id).browse(sale_id)
            company_taxes = so.fiscal_position_id.map_tax(company_taxes, line.product_id, so.partner_id)
        return {
            'name': line.product_id and line.product_id.with_context(lang=lang).name or line.name,
            'order_id': sale_id,
            'product_uom_qty': line.product_qty,
            'product_id': line.product_id and line.product_id.id or False,
            'product_uom': line.product_id and line.product_id.uom_id.id or line.product_uom.id,
            'price_unit': price,
            'customer_lead': line.product_id and line.product_id.sale_delay or 0.0,
            'company_id': company.id,
            'route_id': route_id,
            'tax_id': [(6, 0, company_taxes.ids)],
            'auto_purchase_order_line_id': line.id,
            'line_tag_number': line.line_tag_number,
            'reference_code': line.reference_code,
        }

    @api.multi
    def button_approve(self, force=False):
        for purchase in self:
            if purchase.company_id.country_id != self.env.ref('base.mx'):
                continue
            for line in purchase.order_line:
                if not line.taxes_id:
                    raise UserError('Al menos una linea no tiene impuestos')
        return super(PurchaseOrder, self).button_approve(force=force)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    line_tag_number = fields.Char(
        string='Line item tag number'
    )

    reference_code = fields.Char(
        string='Reference Code'
    )

    @api.multi
    def update_price_po_so(self):
        return {
            'name': 'Update Price',
            'type': 'ir.actions.act_window',
            'res_model': 'update.price.po.so.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': self._context,
        }

    def _onchange_quantity(self):

        super()._onchange_quantity()

        if not self.order_id.businness_partner_id:
            return

        company_rec = self.env['res.company']._find_company_from_partner(self.partner_id.id)
        if not company_rec:
            raise Warning('Error, el proveedor seleccionado no tiene una compañia asignada')

        intercompany_uid = company_rec.intercompany_user_id and company_rec.intercompany_user_id.id or False
        if not intercompany_uid:
            raise Warning(_('Provide at least one user for inter company relation for %s') % company_rec.name)

        pricelist = self.order_id.businness_partner_id.sudo(intercompany_uid).mapped('property_product_pricelist')

        pricelist_item = self.env['product.pricelist.item'].sudo(intercompany_uid).search([
            ('product_id', '=', self.product_id.id),
            ('pricelist_id', '=', pricelist.id),
            ('min_quantity', '<=', self.product_qty)
        ])

        params = {'order_id': self.order_id}
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom,
            params=params)

        price_unit = self.env['account.tax']._fix_tax_included_price_company(
            pricelist_item[0].fixed_price,
            self.product_id.supplier_taxes_id,
            self.taxes_id,
            self.company_id) if pricelist_item else 0.0

        if price_unit and company_rec and self.order_id.currency_id and company_rec.currency_id != self.order_id.currency_id:
            price_unit = company_rec.currency_id._convert(
                price_unit, self.order_id.currency_id, self.order_id.company_id, self.date_order or fields.Date.today())

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)

        self.price_unit = price_unit
