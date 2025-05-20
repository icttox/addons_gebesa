# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, _, fields, models


class MrpBomLineDetail(models.Model):
    _name = 'mrp.bom.line.detail'
    _order = "row"
    _description = 'descripcion pendiente'
    # _rec_name = 'bom_line_id'

    @api.model
    def _default_row(self):
        last_id = 1
        get_count = self.search_count([
            ('bom_line_id', '=', self._context['default_bom_line_id'])])
        if get_count:
            last_id = get_count + 1
        return last_id

    bom_line_id = fields.Many2one(
        'mrp.bom.line',
        string='Parent BoM Line',
        ondelete='cascade',
        index=True,
        # required=True,
    )

    product_id = fields.Many2one(
        'product.product',
        related='bom_line_id.product_id',
        string='Composite Article',
    )

    routing_id = fields.Many2one(
        'mrp.routing',
        string='Manufacturing Routing',
    )

    row = fields.Integer(
        'Row',
        default=_default_row,
        # copy=False,
        help='Gives the row order when displaying.',
    )

    quantity = fields.Float(
        'Quantity',
    )

    width_cut = fields.Float(
        'Cut Width',
        digits=(14, 3)
    )

    thickness = fields.Float(
        'Thickness',
    )

    name = fields.Char(
        string='Name',
    )

    meters2 = fields.Float(
        'Meters2',
        compute='_compute_m2',
        digits=(14, 5)
    )

    material = fields.Many2one(
        'product.product',
        string='Material',
    )

    color_id = fields.Many2one(
        'mrp.product.color',
        string='Color',
        ondelete='restrict',
    )

    caliber_id = fields.Many2one(
        'mrp.product.caliber',
        string='Caliber',
    )

    long_cut = fields.Float(
        'Cut Long',
        digits=(14, 3)
    )

    side = fields.Integer(
        'Sides',
    )

    kilos = fields.Float(
        'Kilos',
        compute='_compute_kilos',
    )

    variants = fields.Char(
        string='Variants',
        # compute='_compute_variants',
        store=True,
    )
    production_line_id = fields.Many2one(
        'mrp.production.line',
        string='Production line',
    )
    attribute_ids = fields.One2many(
        'mrp.bom.line.detail.attribute',
        'line_detail_id',
        string='Attribute',
    )

    _sql_constraints = [
        ('row_uniq', 'unique (bom_line_id, row)',
         _('The row must be unique !')),
    ]

    @api.depends('width_cut', 'long_cut')
    def _compute_m2(self):
        for reg in self:
            width = reg.width_cut / 100
            longs = reg.long_cut / 100
            if not width and longs:
                reg.meters2 = 0.00
            else:
                reg.meters2 = width * longs

    @api.depends('meters2', 'caliber_id')
    def _compute_kilos(self):
        for reg in self:
            if reg.meters2 == 0.00 or not reg.caliber_id:
                return
            reg.kilos = reg.meters2 * reg.caliber_id.peso_kg

    @api.model
    def create(self, vals_list):
        detail = super().create(vals_list)
        detail.create_line_attribute()
        return detail

    @api.multi
    def create_line_attribute(self):
        attribute_obj = self.env['mrp.bom.line.detail.attribute']
        for line in self:
            line.attribute_ids.unlink()
            for value in line.product_id.attribute_value_ids:
                attribute_obj.create({
                    'line_detail_id': line.id,
                    'attribute_id': value.attribute_id.id,
                    'value_ids': [(4, value.id)]
                })

    # @api.depends('bom_line_id.product_id')
    # def _compute_variants(self):
    #     for record in self:
    #         product = self.env['product.product'].search(
    #             [('id', '=', record.bom_line_id.product_id.id)])
    #         prod = product.attribute_value_ids
    #         resul = []
    #         for reg in prod:
    #             name = reg.name
    #             med = self.env['product.attribute'].search(
    #                 [('id', '=', reg.attribute_id.id)])
    #             med_name = med.name
    #             resul.append(str(med_name or '') + " - " + str(name or ''))
    #             lista = tuple(resul)
    #             self.variants = lista

    #         return self.variants


class MrpBomLineDetailAttribute(models.Model):
    _name = 'mrp.bom.line.detail.attribute'
    _rec_name = 'attribute_id'
    _description = 'descripcion pendiente'

    line_detail_id = fields.Many2one(
        'mrp.bom.line.detail',
        string='Bom line detail',
        ondelete='cascade'
    )
    attribute_id = fields.Many2one(
        'product.attribute',
        string='Attribute',
        ondelete='restrict'
    )
    value_ids = fields.Many2many(
        'product.attribute.value',
        'bom_line_detail_attribute_values_rel',
        'detail_attribute_id', 'value_id',
        string='Attribute Values',
    )
