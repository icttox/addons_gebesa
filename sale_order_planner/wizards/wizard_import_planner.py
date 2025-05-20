# -*- coding: utf-8 -*-
# <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from xml.dom.minidom import parseString
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderImportPlanner(models.TransientModel):
    _name = 'sale.order.import.planner'
    _description = 'descripcion pendiente'

    planner_xml = fields.Binary(
        string='Planner',
    )

    @api.multi
    def import_planner(self):
        attachment_obj = self.env['ir.attachment']
        sale_obj = self.env['sale.order']
        sale_line_obj = self.env['sale.order.line']
        product_obj = self.env['product.product']
        pricelist_obj = self.env['product.pricelist.item']
        ir_model_data = self.env['ir.model.data']
        route_obj = self.env['stock.location.route']
        product_product_customer_obj = self.env['product.product.customer']
        generic_product_id = ir_model_data.get_object_reference('sale_order_planner', 'product_generic_planner')[1]
        generic_product = product_obj.browse([generic_product_id])
        partner_planner_id = ir_model_data.get_object_reference('sale_order_planner', 'mpf_2020')[1]

        sale_ids = self._context.get('active_id', False)
        sale = sale_obj.browse(sale_ids)
        company_id = self.env.user.company_id.id
        pricelist = sale.pricelist_id

        try:
            planner_data = base64.decodestring(self.planner_xml)
            dom = parseString(planner_data)
        except Exception:
            raise ValidationError(_("You can not attach this file, it may not be an xml"))

        line_item = dom.getElementsByTagName('ofda:OrderLineItem')

        for item in line_item:
            route_id = False
            price_item = item.getElementsByTagName('ofda:Price')
            product_item = item.getElementsByTagName('ofda:SpecItem')[0].getElementsByTagName('ofda:Alias')
            if not product_item[0].getElementsByTagName('ofda:Number')[0].firstChild:
                raise ValidationError(_('An item in the list does not have a default code'))

            product_code = product_item[0].getElementsByTagName('ofda:Number')[0].firstChild.nodeValue
            product_code = product_code.split("|")
            options = False

            if len(product_code) > 1:
                search_code = product_code[0].strip()
                reference_code = product_code[1].strip()
            else:
                search_code = product_code[0].strip()
                reference_code = False

            product = product_obj.sudo().search(
                [('default_code', '=', search_code),
                 ('active', '=', True)], limit=1)

            if company_id not in product.company_ids.ids:
                product.write({'company_ids': [(4, company_id)]})

            if not product:
                customer_product = product_product_customer_obj.sudo().search(
                    [('customer_code', '=', search_code),
                     ('partner_id', '=', partner_planner_id)], limit=1)
                if customer_product and customer_product.product_id:
                    product = customer_product.product_id
                else:
                    product = generic_product

            if product.family_id:
                route_id = route_obj.search([('family_ids', '=', product.family_id.id)], limit=1)
                if route_id:
                    route_id = route_id.id

            if not item.getElementsByTagName('ofda:Quantity')[0].firstChild:
                raise ValidationError(_('An item in the list does not have a quantity'))

            qty = int(item.getElementsByTagName('ofda:Quantity')[0].firstChild.nodeValue)
            price_list = pricelist_obj.search(
                [('pricelist_id', '=', pricelist.id),
                 ('product_id', '=', product.id),
                 ('min_quantity', '<=', qty)], order="min_quantity desc", limit=1)

            if company_id == 1:
                if not price_list:
                    price = 0
                price = price_list.fixed_price
            else:
                price = float(price_item[0].getElementsByTagName('ofda:OrderDealerPrice')[0].firstChild.nodeValue)

            dealer_order_line = int(item.getElementsByTagName('ofda:LineItemNumber')[0].firstChild.nodeValue)

            tag_line = ''
            tags = item.getElementsByTagName('ofda:Tag')
            for tag in tags:
                tag_type = tag.getElementsByTagName('ofda:Type')[0].firstChild.nodeValue
                if tag_type == 'Tag':
                    if tag.getElementsByTagName('ofda:Value')[0].firstChild:
                        tag_line = tag.getElementsByTagName('ofda:Value')[0].firstChild.nodeValue

            sale_line_obj.create({
                'order_id': sale.id,
                'product_id': product.id,
                'product_uom_qty': qty,
                'price_unit': price,
                'product_uom': product.uom_id.id,
                'route_id': route_id,
                'options': options,
                'dealer_order_line': dealer_order_line,
                'line_tag_number': tag_line,
                'reference_code': reference_code,
            })

        ctx = dict(self._context)
        ctx.pop('default_type', None)

        attachment_obj.with_context(ctx).create({
            'name': 'Planner_' + sale.name + '.xml',
            'datas': self.planner_xml,
            'datas_fname': 'Planner_' + sale.name + '.xml',
            'res_model': 'sale.order',
            'res_id': sale.id
        })
