# -*- coding: utf-8 -*-
# © <2017> <Samuel Barrón Butista>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.multi
    def write(self, vals):
        production_obj = self.env['mrp.production']
        for bom in self:
            production = production_obj.search([
                ('bom_id', '=', bom.id),
                ('state', 'in', ('confirmed', 'ready', 'in_production'))],
                limit=1)
            if production:
                raise UserError(_(
                    'Tiene ordenes de produccion abiertas'))
        return super(MrpBom, self).write(vals)

    @api.multi
    def cancel_production_active(self):
        production_obj = self.env['mrp.production']
        procurement_obj = self.env['procurement.order']
        for bom in self:
            productions = production_obj.search([
                ('bom_id', '=', bom.id),
                ('state', 'in', ('confirmed', 'ready'))])
            for prod in productions:
                procurement = procurement_obj.search([
                    ('production_id', '=', prod.id)])
                procurement.in_review = True
                prod.cancellation_reason = "Cambio de lista de materiales"
                prod.move_prod_id.propagate = False
                prod.action_cancel()

    @api.multi
    def run_procurement_in_review(self):
        procurement_obj = self.env['procurement.order']
        for bom in self:
            procurements = procurement_obj.search([
                ('product_id', '=', bom.product_id.id),
                ('state', '=', 'exception')]).filtered(
                lambda proc: proc.in_review is True)
            for proc in procurements:
                proc.run()
