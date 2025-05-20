# -*- coding: utf-8 -*-
# © <2017> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpBomLineMassiveDelete(models.TransientModel):
    _name = "mrp.bom.line.massive.delete"
    _description = 'descripcion pendiente'

    product_id = fields.Many2one(
        'product.product',
        string='Product Origin',
    )

    @api.multi
    def process(self):
        bom_line_obj = self.env['mrp.bom.line']
        for replacement in self:
            bom_line = bom_line_obj.search(
                [('product_id', '=', replacement.product_id.id)])
            done_ids = []
            # import pdb; pdb.set_trace()
            for line in bom_line:
                if line.bom_id.id in done_ids:
                    continue
                done_ids.append(line.bom_id.id)
                line.unlink()
            # Revaluacion
            for bom in done_ids:
                self.env['mrp.bom'].browse(bom).action_reval()
