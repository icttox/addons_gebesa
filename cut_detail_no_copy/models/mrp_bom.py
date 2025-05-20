# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, _


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.multi
    def action_copy_cut_detail(self):
        bom_dynamic = False
        if self._context and self._context.get('bom_dynamic'):
            bom_dynamic = self._context['bom_dynamic']

        for bom in self:
            copiar = bom.copy()
            for bom_copia in copiar:
                for bom_line_copia in bom_copia.bom_line_ids:
                    if bom_line_copia.bom_line_detail_ids:
                        bom_line_copia.bom_line_detail_ids.unlink()

            if bom_dynamic:
                return copiar

            return {
                'name': _('BoM'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mrp.bom',
                'res_id': copiar.id,
            }
