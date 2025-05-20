# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductUomForchange(models.TransientModel):
    _name = 'product.uom.forchange.wizard'
    _description = 'descripcion pendiente'

    uom_id = fields.Many2one(
        'uom.uom',
        string='Change Unit',
    )

    @api.multi
    def change_uom_id(self):
        res_id = self._context.get('active_ids')
        for res in res_id:
            product_tmpl = self.env['product.template'].browse([res])
            bom_ids = self.env['mrp.bom'].search([
                ('product_tmpl_id', '=', res)])
            uom_origin = product_tmpl.uom_id.name
            self.env.cr.execute("""UPDATE product_template SET uom_po_id = %s , uom_id = %s
                                WHERE id = %s """,
                                (self.uom_id.id, self.uom_id.id, res))
            self.env.cr.execute("""UPDATE mrp_bom SET product_uom_id = %s
                                WHERE product_tmpl_id = %s AND active = True""",
                                (self.uom_id.id, res))
            product_tmpl.message_post(
                body=u"""<ul><li><b>Unidad de medida<b>:
                     %s → %s</b></b></li></ul>""" %
                (uom_origin, self.uom_id.name))
            for bom in bom_ids:
                bom.message_post(
                    body=u"""<ul><li><b>Unidad de medida<b>:
                         %s → %s</b></b></li></ul>""" %
                    (uom_origin, self.uom_id.name))
