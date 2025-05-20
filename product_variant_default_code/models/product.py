# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from string import Template
from collections import defaultdict
from odoo import api, _, fields, models
from odoo.exceptions import except_orm, UserError

DEFAULT_REFERENCE_SEPARATOR = '-'
PLACE_HOLDER_4_MISSING_VALUE = '/'


class ReferenceMask(Template):
    pattern = r'''\[(?:
                    (?P<escaped>\[) |
                    (?P<named>[^\]]+?)\] |
                    (?P<braced>[^\]]+?)\] |
                    (?P<invalid>)
                    )'''


def extract_token(mask):
    pattern = re.compile(r'\[([^\]]+?)\]')
    return set(pattern.findall(mask))


def sanitize_reference_mask(product, mask):
    tokens = extract_token(mask)
    attribute_names = set()
    for line in product.attribute_line_ids:
        attribute_names.add(line.attribute_id.name)
    if not tokens.issubset(attribute_names):
        raise except_orm(_('Error'), _('Found unrecognized attribute name in '
                                       '"Variant Reference Mask"'))


def render_default_code(product, mask):
    # No necesary list every attribute in the mask, retrieves it from the
    # list of attributes of the product
    attr_mask = ""
    # for line in product.attribute_line_ids:
    for line in sorted(product.attribute_line_ids, key=lambda li: li.codebuilder_order):
        attr_mask += ("[" + line.attribute_id.name + "]")

    mask += attr_mask
    product_attrs = defaultdict(str)
    reference_mask = ReferenceMask(mask)
    for value in product.attribute_value_ids:
        if value.attribute_code:
            product_attrs[value.attribute_id.name] += value.attribute_code
    all_attrs = extract_token(mask)
    missing_attrs = all_attrs - set(product_attrs.keys())
    missing = dict.fromkeys(missing_attrs, PLACE_HOLDER_4_MISSING_VALUE)
    product_attrs.update(missing)
    default_code = reference_mask.safe_substitute(product_attrs)
    product.default_code = default_code


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    reference_mask = fields.Char(
        string=_('Variant Reference Mask'),
        copy=False,
        help=_('Reference mask for building internal references of a '
               'variant generated from this template.\n'

               'Example:\n'
               'A product named ABC with 2 attributes: Size and Color:\n'

               'Product: ABC\n'
               'Color: Red(r), Yellow(y), Black(b)  #Red, Yellow, Black are '
               'the attribute value, `r`, `y`, `b` are the corresponding'
               'code\n'
               'Size: L (l), XL(x)\n'

               'When setting Variant reference mask to `[Color]-[Size]`, the '
               'default code on the variants will be something like `r-l` '
               '`b-l` `r-x` ...\n'

               'If you like, You can even have the attribute name appear more'
               'than once in the mask. Such as, `fancyA/[Size]~[Color]~[Size]`'
               'When saved, the default code on variants will be something'
               'like'
               '`fancyA/l~r~l` (for variant with Color "Red" and Size "L") '
               '`fancyA/x~y~x` (for variant with Color "Yellow" and Size "XL")'
               '\n'
               'Note: make sure characters "[,]" do not appear in your '
               'attribute name'))

    @api.multi
    def recreate_default_code(self):
        for prod in self:
            if not prod.reference_mask:
                continue

            cond = [('product_tmpl_id', '=', prod.id),
                    ('manual_code', '=', False)]
            products = self.env['product.product'].search(cond)
            for product in products:
                product.default_code += '_temp0ral'
            for product in products:
                if product.reference_mask:
                    render_default_code(product, product.reference_mask)

    @api.model
    def create(self, vals_list):
        product = self.new(vals_list)
        if not vals_list.get('reference_mask') and product.attribute_line_ids:
            attribute_names = []
            for line in product.attribute_line_ids:
                attribute_names.append("[{}]".format(line.attribute_id.name))
            default_mask = DEFAULT_REFERENCE_SEPARATOR.join(attribute_names)
            vals_list['reference_mask'] = default_mask
        elif vals_list.get('reference_mask'):
            sanitize_reference_mask(product, vals_list['reference_mask'])
        return super().create(vals_list)

    @api.one
    def write(self, vals):
        product_obj = self.env['product.product']
        if 'reference_mask' in vals and not vals['reference_mask']:
            if self.attribute_line_ids:
                attribute_names = []
                for line in self.attribute_line_ids:
                    attribute_names.append("[{}]".format(
                        line.attribute_id.name))
                default_mask = DEFAULT_REFERENCE_SEPARATOR.join(
                    attribute_names)
                vals['reference_mask'] = default_mask
        result = super().write(vals)
        if vals.get('reference_mask'):
            cond = [('product_tmpl_id', '=', self.id),
                    ('manual_code', '=', False)]
            products = product_obj.search(cond)
            for product in products:
                if product.reference_mask:
                    render_default_code(product, product.reference_mask)
        return result

        # Manual

    @api.multi
    def create_standar_price_variant(self):
        for product_tmpl in self:
            for product_variant in product_tmpl.product_variant_ids:
                if product_variant.standard_price == 0.0:
                    product_variant.write({'standard_price': 1})


class ProductProduct(models.Model):
    _inherit = 'product.product'

    manual_code = fields.Boolean(
        string=_('Manual code'))

    @api.model
    def create(self, vals_list):
        product = super().create(vals_list)
        if product.reference_mask:
            render_default_code(product, product.reference_mask)
        return product

    # @api.one
    @api.onchange('default_code')
    def onchange_default_code(self):
        self.manual_code = bool(self.default_code)

    @api.multi
    def unlink(self):
        bom_obj = self.env['mrp.bom']
        for product in self:
            bom = bom_obj.search([('product_id', '=', product.id)])
            if bom:
                raise UserError(
                    _('Error\nThis product already has a bill of materials'))
        return super().unlink()


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    # @api.one
    # @api.onchange('name')
    # def onchange_name(self):
    #     if self.name:
    #         self.attribute_code = self.name[0:2]

    attribute_code = fields.Char(
        string=_('Attribute Code'),
        # default=onchange_name
    )

    @api.model
    def create(self, vals_list):
        if 'attribute_code' not in vals_list:
            vals_list['attribute_code'] = vals_list.get('name', '')[0:2]
        value = super().create(vals_list)
        return value

    @api.one
    def write(self, vals):
        attribute_line_obj = self.env['product.template.attribute.line']
        product_obj = self.env['product.product']
        result = super().write(vals)
        if 'attribute_code' in vals:
            cond = [('attribute_id', '=', self.attribute_id.id)]
            attribute_lines = attribute_line_obj.search(cond)
            for line in attribute_lines:
                cond = [('product_tmpl_id', '=', line.product_tmpl_id.id),
                        ('manual_code', '=', False),
                        ('attribute_value_ids', 'in', self.ids)]
                products = product_obj.with_context(
                    active_test=False).search(cond)
                for product in products:
                    if product.reference_mask:
                        render_default_code(product, product.reference_mask)
        return result


class ProductAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'
    _order = 'sequence'

    sequence = fields.Integer(
        string="Sequence",
        related='attribute_id.sequence',
        store=True
    )

    codebuilder_order = fields.Integer(
        string='Code Builder order',
    )
