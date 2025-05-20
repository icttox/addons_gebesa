# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class MrpShipmentLine(models.Model):
    _inherit = 'mrp.shipment.line'

    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Template',
        compute='_compute_product_tmpl_id',
    )
    packing_id = fields.Many2one(
        'product.packing.list',
        string='Packing List',
    )

    @api.depends('product_id')
    def _compute_product_tmpl_id(self):
        for line in self:
            line.product_tmpl_id = line.product_id.product_tmpl_id.id

    @api.model
    def create(self, vals):
        product_obj = self.env['product.product']
        packing_obj = self.env['product.packing.list']
        product = vals.get('product_id')
        product_var = product_obj.search([('id', '=', product)])
        template = product_var.product_tmpl_id.id
        packing = packing_obj.search([('product_tmpl_id', '=', template),
                                      ('active', '=', True),
                                      ('type', '=', 'standard')])
        if packing:
            vals['packing_id'] = packing.id
        return super(MrpShipmentLine, self).create(vals)
