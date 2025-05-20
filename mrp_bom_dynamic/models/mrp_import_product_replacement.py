# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MrpImportProductReplacement(models.Model):
    _name = 'mrp.import.product.replacement'
    _description = 'Import product replacement'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Code',
        required=True,
        size=64,
    )

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
    )

    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done')],
        string='State',
        default='draft',
    )

    lines_ids = fields.One2many(
        'mrp.import.product.replacement.line',
        'import_product_replacement_id',
        string='Import product replacement line',
    )

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The import product repacement code must be unique"),
    ]

    @api.multi
    def import_product_replacement(self):
        product_obj = self.env['product.product']
        bom_obj = self.env['mrp.bom']
        replacement_obj = self.env['mrp.bom.product.replacement']
        for import_product in self:
            lines = 0
            for line in import_product.lines_ids:
                lines += 1

                product_ori_head = product_obj.search([
                    ('default_code', '=', line.original_header_product)])
                if not product_ori_head:
                    raise UserError(_(
                        'Producto de encabezado original no encontrado: %s \
                        \n Linea: %s' % (line.original_header_product, lines)))

                product_ori_det = product_obj.search([
                    ('default_code', '=', line.original_detail_product)])
                if not product_ori_det:
                    raise UserError(_(
                        'Producto del detalle original no encontrado: %s \
                        \n Linea: %s' % (line.original_detail_product, lines)))

                product_rep_head = product_obj.search([
                    ('default_code', '=', line.replacement_header_product)])
                if not product_rep_head:
                    raise UserError(_(
                        'Producto de encabezado a remplazar no encontrado: %s \
                        \n Linea: %s' % (line.replacement_header_product, lines)))

                product_rep_det = product_obj.search([
                    ('default_code', '=', line.replacement_detail_product)])
                if not product_rep_det:
                    raise UserError(_(
                        'Producto del detalle a remplazar no encontrado: %s \
                        \n Linea: %s' % (line.replacement_detail_product, lines)))

                bom = bom_obj.search([
                    ('product_id', '=', product_ori_head.id),
                    ('active', '=', True)])
                if not bom:
                    raise UserError(_(
                        'No se encontro una lista de materiales activa con el producto: %s \
                        \n Linea: %s' % (line.original_header_product, lines)))

                bom_line_id = bom.mapped('bom_line_ids').filtered(
                    lambda r: (r.product_id.id == product_ori_det.id))
                if not bom_line_id:
                    raise UserError(_(
                        'No se encontro el producto %s en detalle de la lista de \
                        materiales del producto %s \n Linea: %s' % (
                            line.original_detail_product,
                            line.original_header_product,
                            lines)))

                product_replacement = bom_line_id.mapped(
                    'bom_line_product_value_ids').filtered(
                    lambda r: (r.bom_product_id.id == product_rep_head.id))

                if product_replacement:
                    raise UserError(_(
                        'El producto %s ya tiene asignado un producto de remplazo\
                        \n Linea: %s' % (line.replacement_header_product, lines)))

                replacement_obj.create({
                    'bom_line_value_id': bom_line_id.id,
                    'bom_product_id': product_rep_head.id,
                    'product_id': product_rep_det.id
                })

            import_product.state = 'done'

    @api.multi
    def unlink(self):
        for import_product in self:
            if import_product.state == 'done':
                raise UserError(_(
                    'No puede borrar una importacion ya confirmada'))
        return super(MrpImportProductReplacement, self).unlink()


class MrpImportProductReplacementLine(models.Model):
    _name = 'mrp.import.product.replacement.line'
    _description = 'Import product replacement line'

    import_product_replacement_id = fields.Many2one(
        'mrp.import.product.replacement',
        string='Import product replacement',
        ondelete='cascade',
    )
    original_header_product = fields.Char(
        string='Producto encabezado original',
        required=True,
    )
    original_detail_product = fields.Char(
        string='Producto del detalle original',
        required=True,
    )
    replacement_header_product = fields.Char(
        string='Producto encabezado a remplazar',
        required=True,
    )
    replacement_detail_product = fields.Char(
        string='Producto del detalle a remplazar',
        required=True,
    )
