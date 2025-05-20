# Copyright 2024, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MrpProduction(models.Model):
    _name = 'mrp.production'
    _inherit = 'mrp.production'

    def production_workorder_planner(self):
        productions = self.search([
            ('state', '=', 'confirmed'),
            ('workorder_ids', '=', False),
            ('routing_id', '!=', False)])
        productions = productions.filtered(
            lambda pro: pro.routing_id.operation_ids)
        productions.button_plan()
