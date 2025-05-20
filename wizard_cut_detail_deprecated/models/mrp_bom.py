# -*- coding: utf-8 -*-
# © <2017> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, _


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.multi
    def print_wizard(self):
        # import pdb; pdb.set_trace()
        ctx = self.env.context.copy()
        ctx.update({'default_bom_id': self.id})
        return {
            'name': _('Report Cut Detail'),
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.cut.detail',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': ctx,
        }
