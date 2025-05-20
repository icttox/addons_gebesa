# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class BomDeleteMassiveImport(models.Model):
    _name = 'bom.delete.massive.import'
    _description = 'Bom Delete Massive Import'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Code',
        size=64,
    )

    date = fields.Date(
        string='Date',
        default=fields.Date.today,
    )

    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done')],
        string='State',
        default='draft',
    )

    lines_ids = fields.One2many(
        'bom.delete.massive.import.line',
        'bom_delete_massive_id',
        string='Bom Delete Massive lines',
    )

    @api.multi
    def delete_bom_massive(self):
        product_mas_obj = self.env['product.product']
        bom_obj = self.env['mrp.bom']

        for massive in self:
            done_ids = []
            for line in massive.lines_ids:

                # Producto existe con clave dada y es válido?
                prod = product_mas_obj.search(
                    [('default_code', '=', line.code_master),
                     ('active', '=', True)])
                if not prod:
                    message_body = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (_("No key is found"), line.code_master)
                    massive.message_post(body=message_body)
                    continue

                bomm = bom_obj.search(
                    [('product_id', '=', prod.id),
                     ('active', '=', True)])
                # Tiene bom ?
                if not bomm.product_id:
                    message_body_bomm = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (_("Product has no valid path"),line.code_current)
                    massive.message_post(body=message_body_bomm)
                    continue

                for bom_line in bomm.bom_line_ids:
                    bom_line.unlink()

                if bomm.id in done_ids:
                    continue
                done_ids.append(bomm.id)

            # Revaluacion
            for bom in done_ids:
                self.env['mrp.bom'].browse(bom).action_reval()
            massive.state = 'done'


class BomDeleteMassiveImportLine(models.Model):
    _name = 'bom.delete.massive.import.line'
    _description = 'Bom Delete Massive Import Line'

    bom_delete_massive_id = fields.Many2one(
        'bom.delete.massive.import',
        string='Bom Delete Massive Import',
        ondelete='cascade',
        index=2,
        required=True,
    )

    code_master = fields.Char(
        string='Code Master',
        required=True,
    )
