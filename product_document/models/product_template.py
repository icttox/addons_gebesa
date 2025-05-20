# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_document_ids = fields.One2many(
        'product.document',
        'product_template_id',
        string='Product Document',
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def get_upper_products_ids(self):

        query = """
            WITH RECURSIVE prodcts AS (
                  SELECT pp.id,
                  pp.default_code,
                  pp.product_tmpl_id
                  FROM mrp_bom_line mbl
                  JOIN mrp_bom mb ON mb.id = mbl.bom_id
                  JOIN product_product pp on pp.id = mb.product_id
                  WHERE mbl.product_id in (%s)
               UNION ALL
                  SELECT pp.id,
                  pp.default_code,
                  pp.product_tmpl_id
                  FROM mrp_bom_line mbl
                  JOIN mrp_bom mb ON mb.id = mbl.bom_id
                  JOIN product_product pp on pp.id = mb.product_id
                  JOIN prodcts ON mbl.product_id in (prodcts.id)
            )
            SELECT * FROM prodcts;
        """

        self.env.cr.execute(query, self.ids)
        res = self.env.cr.fetchall()
        return res

    @api.multi
    def action_view_product_documents(self):

        upper_products = self.get_upper_products_ids()

        tmpl_ids = [rec[2] for rec in upper_products]

        tmpscur = self.mapped('product_tmpl_id').ids

        ids = tmpl_ids + tmpscur

        doctos = self.env['product.document'].search([
            ('product_template_id', 'in', ids)]).ids

        action = self.env.ref(
            'product_document.product_document_action').read()[0]
        action['domain'] = [('id', 'in', doctos)]
        return action
