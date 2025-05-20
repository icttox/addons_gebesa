# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.one
    @api.constrains('default_code')
    def _check_default_code(self):
        product = self.env['product.product'].search(
            [('default_code', '=', self.default_code),
             ('active', '=', True),
             ('id', '!=', self.id)]) or False
        if product:
            raise ValidationError(_("The field Internal Reference must be"
                                  " unique!"))

    # _sql_constraints = [
    #     ('default_uniq', 'unique (default_code)',
    #      _('The field Internal Reference must be unique!')),

    # ]
