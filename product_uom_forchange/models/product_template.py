# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def send_uom(self):
        return {
            'name': _('Product Uom Forchange'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.uom.forchange.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': self._context,
        }
