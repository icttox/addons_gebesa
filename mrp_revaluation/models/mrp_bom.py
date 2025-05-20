# -*- coding: utf-8 -*-
# © <2016> <Cesar Barron>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError


class MrpBom(models.Model):
    _name = "mrp.bom"
    _inherit = "mrp.bom"

    @api.one
    @api.depends('product_id', 'product_tmpl_id')
    def _get_stdcost(self):
        if self.product_id and self.product_id.id:
            self.product_cost = self.product_id.standard_price
        elif self.product_tmpl_id and self.product_tmpl_id.id:
            self.product_cost = self.product_tmpl_id.standard_price
        else:
            self.product_cost = 0.00

    product_cost = fields.Float(
        string='Product Cost',
        required=True,
        compute=_get_stdcost)

    @api.one
    def action_reval(self):
        """ Apply the revaluation
        @return: True
        """
        for rec in self:
            totcost = 0.00

            for line in rec.bom_line_ids:
                totcost += (line.amount)

            product_accounts = rec.product_tmpl_id.get_product_accounts()
            rec.product_tmpl_id.create_standar_price_variant()

            if rec.product_id:
                rec.product_id.do_change_standard_price2(
                    [rec.product_id.id],
                    totcost)
            elif rec.product_tmpl_id:
                if len(rec.product_tmpl_id.product_variant_ids) > 1:
                    raise UserError(
                        'El bom para el product %s no tiene difinida la variante' % rec.product_tmpl_id.name)
                rec.product_tmpl_id.product_variant_ids.do_change_standard_price2(
                    rec.product_tmpl_id.product_variant_ids.ids, totcost)
        return True

    # @api.model
    # def create(self, vals):
    #     res = super(MrpBom, self).create(vals)
    #     if not self._context.get('bom_dynamic', False):
    #         res.action_reval()
    #     return res

    # @api.multi
    # def write(self, values):
    #     # revaluacion
    #     res = super(MrpBom, self).write(values)
    #     if not self._context.get('bom_dynamic', False):
    #         self.action_reval()
    #     return res


class MrpBomLine(models.Model):
    _name = "mrp.bom.line"
    _inherit = "mrp.bom.line"

    @api.one
    @api.depends('product_id')
    def _get_stdcost(self):
        if self.product_id and self.product_id.id:
            self.product_cost = self.product_id.standard_price
        else:
            self.product_cost = 0.00

    @api.one
    @api.depends('product_id')
    def _get_amount_line(self):
        if self.product_id and self.product_id.id:
            self.amount = self.product_id.standard_price * self.product_qty
        else:
            self.amount = 0.00

    product_cost = fields.Float(
        string='Product Cost',
        required=True,
        compute=_get_stdcost)

    amount = fields.Float(
        string='Amount',
        required=True,
        compute=_get_amount_line)
