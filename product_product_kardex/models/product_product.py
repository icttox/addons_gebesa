# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def print_kardex(self):
        ctx = self.env.context.copy()
        ctx.update({'default_product_id': self.id})
        return {
            'name': _('Product Kardex Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.product.kardex.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'context': ctx,
        }
