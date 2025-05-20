# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class StockChangeStandardPrice(models.TransientModel):
    _name = "stock.change.standard.price"
    _inherit = "stock.change.standard.price"
    _description = "Change Standard Price"

    @api.multi
    def change_price(self):
        """Change the Standard Price of Product and creates an account move accordingly."""
        self.ensure_one()
        if self.new_price <= 0.00:
            raise UserError(
                _('The new cost has to be greater than zero'))
        if self._context['active_model'] == 'product.template':
            bom_as_tmpl = self.env['mrp.bom'].search([(
                'product_tmpl_id', "=", self._context['active_id'])])
            if bom_as_tmpl:
                raise UserError(
                    _('You cannot change manually a standard cost '
                      'of a product with Bill of Materials.'))
            products = self.env['product.template'].browse(
                self._context['active_id']).product_variant_ids
        else:
            products = self.env['product.product'].browse(
                self._context['active_id'])
            bom_as_tmpl = self.env['mrp.bom'].search([(
                'product_tmpl_id', "=", products.product_tmpl_id.id)])
            if bom_as_tmpl:
                raise UserError(
                    _('You cannot change manually a standard cost '
                      'of a product with Bill of Materials.'))

        products.do_change_standard_price2(
            products.ids, self.new_price)
        return {'type': 'ir.actions.act_window_close'}
