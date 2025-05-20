# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_line = fields.Boolean(
        string='Line Product',
        copy=False,
        default=False,
    )

    family_id = fields.Many2one(
        'product.family',
        string='Family',
    )

    group_id = fields.Many2one(
        'product.group',
        string='Group',
    )

    line_id = fields.Many2one(
        'product.line',
        copy=False,
        string='Line',
    )

    type_id = fields.Many2one(
        'product.type',
        string='Type',
    )
    cutting_detail = fields.Boolean(
        string='Requires cutting detail',
    )
    multi_variant = fields.Boolean(
        string='Multi Variant',
        compute='_compute_product_variant_count'
    )

    type_product = fields.Selection(
        [('special', 'Especial'),
         ('semi_special', 'Semiespecial')],
        string='Producto de tipo',
    )

    @api.one
    @api.depends('product_variant_ids.product_tmpl_id')
    def _compute_product_variant_count(self):
        super()._compute_product_variant_count()
        self.multi_variant = False
        if self.product_variant_count > 1:
            self.multi_variant = True

    @api.model
    def _get_buy_route(self):
        # make_route = self.env.ref('stock.route_warehouse0_mto', raise_if_not_found=False)
        default_routes = self.env['stock.location.route'].search(
            [('route_default', '=', True),
             ('company_id', '=', self.env.user.company_id.id)])
        if default_routes:
            return default_routes.ids
        return []
