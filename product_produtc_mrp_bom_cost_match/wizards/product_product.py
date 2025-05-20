# -*- coding: utf-8 -*-
# Copyright 2018, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

class BatchProductBomCodes(models.TransientModel):
    _name = 'batch.product.bom.codes'
    _description = u'gruop of products for match cost with their BoM'

    pp_codes = fields.Text(
        string='Products to match cost',
        required=True,)

    @api.multi
    def action_match_cost_all(self):

        prodObj = self.env['product.product']
        bomObj = self.env['mrp.bom']

        for rec in self:
            split_codes = rec.pp_codes.split(',')

            for clave in split_codes:
                products = self.env[
                    'product.product'].search(
                        [('default_code', '=', clave)], limit=1)

                if not products:
                    continue

                prod = products[0]

                boms = self.env[
                    'mrp.bom'].search(
                        [('product_id', '=', prod.id),
                         ('active', '=', True)], limit=1)

                if not boms:
                    continue

                detalle = boms[0]

                detalle.action_reval()

                self.env.cr.commit()
        return True
