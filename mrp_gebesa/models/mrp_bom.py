# -*- coding: utf-8 -*-
# © <2016> Cesar barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpBom(models.Model):
    _name = "mrp.bom"
    _inherit = "mrp.bom"

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        required=True)

    ready_to_produce = fields.Selection([
        ('all_available', ' When all components are available'),
        ('asap', 'When components for 1st operation are available')],
        string='Manufacturing Readiness',
        default='all_available',
        help="Defines when a Manufacturing Order is considered as ready to be started", required=True)

    @api.multi
    def unlink(self):
        for bom in self:
            if bom.bom_line_ids:
                raise UserError(_('This BOM has detail'))
        return super().unlink()

    @api.multi
    def write(self, vals):
        for rec in self:
            if 'type' in vals.keys():
                types = vals['type']
            else:
                types = rec.type

            if 'warehouse_id' in vals.keys():
                ware_obj = self.env['stock.warehouse']
                ware = ware_obj.browse(vals['warehouse_id'])
            else:
                ware = rec.warehouse_id

            if 'routing_id' in vals.keys():
                routing_obj = self.env['mrp.routing']
                routing = routing_obj.browse(vals['routing_id'])
            else:
                routing = rec.routing_id

            if 'product_id' in vals.keys():
                producto_obj = self.env['product.product']
                product = producto_obj.browse(vals['product_id'])

            else:
                product = rec.product_id

            route_ids = []
            manuf_ids = self.env['stock.location.route'].search(
                [('is_manufacture', '=', True)]).ids
            buy_id = self.env.ref('purchase_stock.route_warehouse0_buy').id
            if 'product_tmpl_id' in vals.keys():
                # se construye el objeto, y los busca por medio del vals
                template = self.env['product.template'].browse(
                    vals['product_tmpl_id'])
                # condicion para la busquedan
                route_ids = template.mapped('route_ids').mapped('id')
                if not any(x in manuf_ids for x in route_ids):
                    if buy_id in route_ids:
                        raise UserError(_('This product is raw material'))

                rec.onchange_product_tmpl_id()
            else:
                template = rec.product_tmpl_id

            if types == 'normal':
                if ware.id != routing.location_id.stock_warehouse_id.id:
                    raise UserError(_('The production route must'
                                      ' be in the same warehouse than the bom'))
                if rec.product_tmpl_id:
                    rec.product_tmpl_id.sudo().write({
                        'invoice_policy': 'delivery'
                    })
            if types == 'phantom':
                if routing.id != 0:
                    raise UserError(_('Kit products should not have route production'))
                if rec.product_tmpl_id:
                    rec.product_tmpl_id.sudo().write({
                        'invoice_policy': 'order'
                    })

            if template.id != product.product_tmpl_id.id:
                raise UserError(_('Product and template it does not match'))
        return super().write(vals)

    @api.model
    def create(self, vals_list):
        # objeto para no guardar variantes ya existentes
        # bom_obj = self.env['mrp.bom']
        ware_obj = self.env['stock.warehouse']
        routing_obj = self.env['mrp.routing']
        producto_obj = self.env['product.product']
        template = self.env['product.template'].browse(vals_list['product_tmpl_id'])
        ware = ware_obj.browse(vals_list['warehouse_id'])
        routing = routing_obj.browse(vals_list['routing_id'])
        route_ids = []
        manuf_ids = self.env['stock.location.route'].search(
            [('is_manufacture', '=', True)]).ids
        buy_id = self.env.ref('purchase_stock.route_warehouse0_buy').id
        if 'product_id' in vals_list.keys():
            product = producto_obj.browse(vals_list['product_id'])
            if template.id != product.product_tmpl_id.id:
                raise UserError(_('Product and template it does not match'))
        # objeto de busqueda para ver si ya existe
        # bom_id = bom_obj.search([('product_id', "=", vals_list['product_id']),
        #                         ('active', '=', True)])
        # if len(bom_id) > 0:
        #    raise UserError(_('This product is already exists'))
        if vals_list['type'] == 'normal':
            if ware.id != routing.location_id.stock_warehouse_id.id:
                raise UserError(_('The production route must'
                                  'be in the same warehouse than the bom'))
            if template:
                template.sudo().write({
                    'invoice_policy': 'delivery'
                })
        if vals_list['type'] == 'phantom':
            if routing.id != 0:
                raise UserError(_('Kit products should not have route production'))
            if template:
                template.sudo().write({
                    'invoice_policy': 'order'
                })

        route_ids = template.mapped('route_ids').mapped('id')
        if not any(x in manuf_ids for x in route_ids):
            if buy_id in route_ids:
                raise UserError(_('This product is raw material'))
        # for route in val.route_ids:
        #     if route.id == 6:
        #         raise UserError(_('This product is raw material'))

        res = super().create(vals_list)

        for bom in res:
            bom.onchange_product_tmpl_id()

        return res


class MrpBomLine(models.Model):
    _name = "mrp.bom.line"
    _inherit = "mrp.bom.line"

    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        required=True)

    @api.model
    def create(self, vals_list):
        bom_obj = self.env['mrp.bom']
        product_obj = self.env['product.product']
        location_obj = self.env['stock.location']
        # warehouse_obj = self.env['stock.warehouse']
        if 'bom_id' in vals_list.keys():
            bom = bom_obj.browse([vals_list['bom_id']])
            product = product_obj.browse([vals_list['product_id']])
            if bom.company_id.is_manufacturer:
                location = location_obj.browse([vals_list['location_id']])
                # buscamos BoM del articulo (detalle) a agregar
                product_bom = bom_obj.search([
                    ('product_id', '=', vals_list['product_id'])])
                if bom.type == 'phantom':
                    # No se pueden agregar productos sin detalle a los Kits
                    if not product_bom:
                        raise UserError(_('You can not add a product that \
                            has no BOM: %s') % (product.name,))
                else:
                    if location.type_stock_loc == 'fp':
                        raise UserError(_('You can not add a PT detail if this is not a Kit: %s')
                                        % (product.name,))

                if product.standard_price == 0.000000:
                    raise UserError(_('You can not add a product with cost 0: %s')
                                    % (product.name,))

                if location.type_stock_loc == 'rm' and product_bom and product_bom.warehouse_id.id == bom.warehouse_id.id:
                    raise UserError(_('You can not add a MP detail with this product, it is made in this warehouse: %s')
                                    % (product.name,))
                if location.type_stock_loc == 'wip' and (not product_bom or product_bom.warehouse_id.id != bom.warehouse_id.id):
                    raise UserError(_('You can not add a product without BoM in this location: %s')
                                    % (product.name,))

            if product.id == bom.product_id.id:
                raise UserError(_('One product cannot be detail of itself'))
            for line in bom.bom_line_ids:
                if line.product_id.id == product.id:
                    raise UserError(_('This product is already in this Bom'))
        return super().create(vals_list)

    @api.multi
    def write(self, vals):
        # if 'bom_id' in vals.keys() and self._uid in (1, 37, 38, 86, 107):
        #     return
        bom_obj = self.env['mrp.bom']
        product_obj = self.env['product.product']
        location_obj = self.env['stock.location']

        if 'product_id' in vals.keys() or 'location_id' in vals.keys():
            if 'product_id' in vals.keys():
                product = product_obj.browse([vals['product_id']])
            else:
                product = product_obj.browse([self.product_id.id])

            if 'bom_id' in vals.keys():
                bom = bom_obj.browse([vals['bom_id']])
            else:
                bom = bom_obj.browse([self.bom_id.id])

            if bom.company_id.is_manufacturer:
                if 'location_id' in vals.keys():
                    location = location_obj.browse([vals['location_id']])
                else:
                    location = location_obj.browse([self.location_id.id])

                product_bom = bom_obj.search([
                    ('product_id', '=', product.id),
                    ('active', '=', True)], limit=1)
                if bom.type == 'phantom':
                    # No se pueden agregar productos sin detalle a los Kits
                    if not product_bom:
                        raise UserError(_('You can not add a product that \
                            has no BOM: %s') % (product.name,))
                else:
                    if location.type_stock_loc == 'fp':
                        raise UserError(_('You can not add a PT detail if this is not a Kit: %s')
                                        % (product.name,))
                if product.standard_price == 0.000000:
                    raise UserError(_('You can not add a product with cost 0: %s')
                                    % (product.name,))
                if location.type_stock_loc == 'rm' and product_bom and product_bom.warehouse_id.id == bom.warehouse_id.id:
                    raise UserError(_('You can not add a MP detail with this product, it is made in this warehouse: %s')
                                    % (product.name,))
                if location.type_stock_loc == 'wip' and (not product_bom or product_bom.warehouse_id.id != bom.warehouse_id.id):
                    raise UserError(_('You can not add a product without BoM in this location: %s')
                                    % (product.name,))

            if product.id == bom.product_id.id:
                raise UserError(_('One product cannot be detail of itself'))

            bom_dynamic = False
            if self._context and self._context.get('bom_dynamic'):
                bom_dynamic = self._context['bom_dynamic']

            for line in bom.bom_line_ids:
                if not bom_dynamic:
                    if line.product_id.id == product.id and line.id != self.id:
                        raise UserError(_('This product is already in this Bom'))

        return super().write(vals)
