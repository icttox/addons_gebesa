# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date

from odoo import api, fields, models
from odoo.exceptions import UserError


class UpdatePricePoSoWizard(models.TransientModel):
    _name = 'update.price.po.so.wizard'
    _description = 'descripcion pendiente'

    new_price = fields.Float(
        string='New Price',
    )

    @api.multi
    def apply_new_price(self):
        purchase_line_obj = self.env['purchase.order.line']
        sale_line_obj = self.env['sale.order.line']
        active_ids = self._context.get('active_ids', []) or []
        purchase_line_ids = purchase_line_obj.browse(active_ids)
        ctx = self._context.copy()
        ctx.update({'update_so_price_intercompany': True})
        for line in purchase_line_ids:
            sale_line_ids = sale_line_obj.sudo().search([
                ('auto_purchase_order_line_id', '=', line.id)])

            if sale_line_ids.qty_invoiced > 0:
                raise UserError(
                    "La linea del producto %s ya esta facturada, no puede cambiar el precio" % line.product_id.default_code)

            price_unit = line.price_unit
            line.write({'price_unit': self.new_price})
            message_body = """
                <b>Precio Actualizado</b><br/>
                    Producto %s (linea %s): %s -> %s""" % (
                line.product_id.default_code, line.id,
                price_unit, self.new_price)
            line.order_id.message_post(body=message_body)

            if sale_line_ids:
                state = sale_line_ids[0].order_id.state
                if state == 'done':
                    sale_line_ids.order_id.sudo().write({
                        'state': 'sale'})

                sale_line_ids.sudo().with_context(ctx).write({
                    'price_unit': self.new_price})

                sale_line_ids.order_id.sudo().write({
                    'state': state})

                message_body = """
                    <b>Precio Actualizado por %s</b><br/>
                        Producto %s (linea %s): %s -> %s""" % (
                    self.env.user.name, sale_line_ids.product_id.default_code,
                    sale_line_ids.id, price_unit, self.new_price)
                sale_line_ids.order_id.message_post(body=message_body)

                responsible = self.env['res.users'].sudo().search([
                    ('login', '=', 'monica.sanchez@gebesa.com')], limit=1)
                sale_line_ids.order_id.activity_schedule(
                    'mail.mail_activity_data_warning',
                    date.today(),
                    note=message_body,
                    user_id=responsible[0].id or self.env.user.id
                )

                sale_line_ids.order_id.calculate_profit_margin()
