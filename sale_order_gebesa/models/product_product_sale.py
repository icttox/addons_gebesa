# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    sale_product_quantity = fields.Integer(
        string=('Cantidad a vender'),
    )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    type = fields.Selection(default='product')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        for sale in self:
            _logger.error(
                _('sale_order_gebesa_product_product_sale ini: %s' % sale.name))

            for line in sale.order_line:
                cantidad_ped = line.product_uom_qty
                product_ped = line.product_id.sale_product_quantity
                product_ped = float(product_ped)
                if cantidad_ped < product_ped and cantidad_ped > 0:
                    raise UserError(
                        ("La cantidad minima a vender del producto: %s es: %s" % (line.product_id.default_code, product_ped)))
                if product_ped > 0 and cantidad_ped >= product_ped:
                    resto = cantidad_ped % product_ped
                    if resto != 0:
                        raise UserError(_("Este producto solo puede vender multiplos de %s") % product_ped)
            _logger.error(
                _('sale_order_gebesa_product_product_sale ini: %s' % sale.name))
        return super().action_confirm()
