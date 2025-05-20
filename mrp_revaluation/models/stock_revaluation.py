# -*- coding: utf-8 -*-
# © <2016> <Cesar Barron>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from ast import literal_eval
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import odoo.addons.decimal_precision as dp


REVALUATION_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('cancel', 'Cancelled'),
    ('confirm', 'In Progress'),
    ('done', 'Validated')]


class StockRevaluation(models.Model):
    _name = "stock.revaluation"
    _description = "Revaluation"

    def _default_stock_location(self):
        try:
            warehouse = self.env['ir.model.data'].get_object(
                'stock', 'warehouse0')
            return warehouse.lot_stock_id.id
        except:
            return False

    name = fields.Char(
        string='Revaluation Reference',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Inventory Name.")

    date = fields.Datetime(
        string='Revaluation Date',
        required=True,
        readonly=True,
        default=fields.Datetime.now,
        help='The date that will be used for the '
        'revaluation of the products and the validation '
        'of the account move related to this inventory.')

    line_ids = fields.One2many(
        'stock.revaluation.line',
        'revaluation_id',
        string='Revaluated Products',
        readonly=False,
        states={'done': [('readonly', True)]},
        help="Revaluation Lines.",
        copy=True)

    move_ids = fields.Many2many(
        'account.move',
        help="Account Moves.",
        states={'done': [('readonly', True)]})

    state = fields.Selection(
        REVALUATION_STATE_SELECTION,
        string='Status',
        readonly=True,
        index=True,
        default='draft',
        copy=False)

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        index=True,
        readonly=True,
        default=lambda self: self.env.user.company_id,
        states={'draft': [('readonly', False)]})

    location_id = fields.Many2one(
        'stock.location',
        string='Revaluated Location',
        required=True,
        readonly=True,
        default=_default_stock_location,
        states={'draft': [('readonly', False)]})

    prod_category_id = fields.Many2one(
        'product.category',
        string='Product Category',
        required=False,
        readonly=True,
        states={'draft': [('readonly', False)]})

    prod_group_id = fields.Many2one(
        'product.group',
        string='Product Group',
        required=False,
        readonly=True,
        states={'draft': [('readonly', False)]})

    prod_line_id = fields.Many2one(
        'product.line',
        string='Product Line',
        required=False,
        readonly=True,
        states={'draft': [('readonly', False)]})

    @api.one
    def reset_real_cost(self):
        for line in self.line_ids:
            line.write(
                {'product_cost': line.product_id.standard_price,
                 'comments': ''})
        return True

    @api.one
    def action_done(self):
        """ Apply the revaluation
        @return: True
        """
        for rev in self:
            for rev_line in rev.line_ids:
                if rev_line.product_cost < 0:
                    raise UserError(_(
                        'You cannot set a negative product '
                        'cost in an revaluation line:\n\t%s - cost: %s') % (
                            rev_line.product_id.name,
                            rev_line.product_cost))

            self.action_check()
            self.write({'state': 'done'})
            self.post_revaluation()
        return True

    def post_revaluation(self):
        # Auxiliar method to do something useful after revaluation
        # Hook me
        return True

    def action_check(self):
        """ Checks the revaluation and computes what to do
        @return: True
        """
        for rev in self:
            for line in rev.line_ids:
                # compare the checked cost on revaluation lines to the
                # actual_cost one
                if line.difference != 0:
                    line._perform_revaluation_line()
        return True

    @api.one
    def prepare_revaluation(self):
        for rev in self:
            # If there are revaluation lines already (e.g. from import),
            # respect those and set their actual cost
            line_ids = [line.id for line in rev.line_ids]
            if not line_ids:
                # compute the revaluation lines and create them
                vals = self._get_revaluation_lines()

                for product_line in vals:
                    self.env[
                        'stock.revaluation.line'].create(product_line)

        return self.write({'state': 'confirm',
                          'date': time.strftime(
                                    DEFAULT_SERVER_DATETIME_FORMAT)})

    def _get_revaluation_lines(self):
        domain = [
            ('location_id', '=', self.location_id.id),
            ('product_id.type', 'in', ["product"])]

        if self.prod_group_id:
            domain += [('product_id.group_id', '=', self.prod_group_id.id)]
        if self.prod_line_id:
            domain += [('product_id.line_id', '=', self.prod_line_id.id)]

        quants = self.env['stock.quant'].search(domain)

        # product_ids = []
        # for quant in quants:
        #     product_ids.append(quant.product_id.id)

        # products = self.env['product.product'].browse(product_ids)
        products = quants.mapped('product_id')

        vals = []
        for product in products:
            # Se comprueba si tiene codigo
            if not product.default_code:
                continue

            # Se comprueba si existe bom, por template y product, si trae valor,
            # Seguira con el siguiente, sino que lo guarde en un diccionario
            self._cr.execute("""
                SELECT mb.id
                    FROM mrp_bom as mb
                    WHERE mb.product_id = %s
                        AND mb.active = True""", [product.id])
            if self._cr.rowcount:
                continue

            self._cr.execute("""
                SELECT mb2.id
                    FROM mrp_bom as mb2
                    WHERE mb2.product_tmpl_id = %s
                        AND mb2.active = True""", [product.product_tmpl_id.id])
            if self._cr.rowcount:
                continue

            product_line = dict(
                (fn, 0.0) for fn in [
                    'revaluation_id', 'product_id',
                    'product_cost', 'comments'])
            # replace the None the dictionary by False, because falsy values
            # are tested later on
            product_line['revaluation_id'] = self.id
            product_line['product_id'] = product.id
            product_line['product_cost'] = product.standard_price
            product_line['comments'] = ''
            vals.append(product_line)
        return vals


class StockRevaluationLine(models.Model):
    _name = "stock.revaluation.line"
    _description = "Revaluation Line"
    _order = 'revaluation_id, product_code, product_name'

    revaluation_id = fields.Many2one(
        'stock.revaluation',
        string='Revaluation',
        ondelete='cascade',
        index=True)

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        index=True)

    product_cost = fields.Float(
        string='New Cost',
        digits=dp.get_precision('Product Price'))

    difference = fields.Float(
        string='Difference',
        compute='_calculate_difference')

    company_id = fields.Many2one(
        string='Company',
        related='revaluation_id.company_id',
        store=True)

    state = fields.Selection(
        REVALUATION_STATE_SELECTION,
        string='State',
        related='revaluation_id.state',
        store=True)

    actual_cost = fields.Float(
        string='Actual Cost',
        related='product_id.standard_price',
        store=True)

    product_name = fields.Char(
        string='Name',
        related='product_id.name',
        store=True)

    product_code = fields.Char(
        string='Name',
        related='product_id.default_code',
        store=True)

    product_cat_id = fields.Many2one(
        string='Category',
        related='product_id.categ_id',
        store=True)

    comments = fields.Char(
        string='Comments',
        states={'draft': [('readonly', False)]},
        help="Comments.")

    def create(self, vals):
        dom = [('product_id', '=', vals.get('product_id')),
               ('revaluation_id.state', '=', 'confirm')]

        res = self.search(dom)

        if res:
            product = self.env['product.product'].browse(
                vals.get('product_id'))
            raise UserError(
                _('You cannot have two revaluations in '
                  'state "in Progess" with the same '
                  'product(%s). Please first validate the '
                  'first revaluation with this product '
                  'before creating another one.') % (product.name))

        return super(StockRevaluationLine, self).create(vals)

    @api.depends('actual_cost', 'product_cost')
    def _calculate_difference(self):
        for rec in self:
            rec.difference = rec.product_cost - rec.actual_cost

    @api.onchange('difference')
    def _onchange_difference(self):
        perce_dif = literal_eval(self.env[
            'ir.config_parameter'].sudo().get_param(
                'mrp_revaluation.perc_revaluation', 'False'))
        for line in self:
            diff = line.actual_cost * (perce_dif / 100.00)
            if line.difference > diff:
                return {
                    'warning': {
                        'title': _(u"Error"),
                        'message':
                        _(u"The difference is greater than that allowed for \
                            this product"),
                    },
                }

    @api.constrains('product_cost')
    def _check_actual_cost(self):
        perce_dif = literal_eval(self.env[
            'ir.config_parameter'].sudo().get_param(
                'mrp_revaluation.perc_revaluation', 'False'))
        for line in self:
            diff = line.actual_cost * (perce_dif / 100.00)
            if line.difference > diff:
                raise ValidationError("The difference is greater than that \
                    allowed")

    def _perform_revaluation_line(self):
        self.product_id.do_change_standard_price2(
            rec_ids=self.product_id.id, new_price=self.product_cost)
        return True
