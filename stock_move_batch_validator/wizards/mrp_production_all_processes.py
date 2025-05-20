# -*- coding: utf-8 -*-
# © 2017 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class MrpProductionAllProcesses(models.TransientModel):
    _name = 'mrp.production.all.processes'
    _description = 'mrp production for procurement, produce and tranfer'

    @api.multi
    def action_all_processes(self):
        active_ids = self._context.get('active_ids', []) or []
        productions = self.env['mrp.production'].browse(active_ids)
        productions.action_all_processes()
