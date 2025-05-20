# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Para la version 12 desaparece el estatus parcialmente disponible
    # tenemos este estatus de disponibilidad para determinar
    # cuando mostrar el boton de forzar disponibilidad
    gavailavility = fields.Char(
        string='Availavility',
        compute='_determine_availibility',
        # store=True,
    )

    @api.multi
    def _determine_availibility(self):
        for pick in self:
            moves_todo = pick.move_lines\
                .filtered(lambda move: move.state not in ['cancel', 'done'])
            if not moves_todo:
                pick.gavailavility = 'assigned'
            else:
                pick.gavailavility = pick.move_lines._get_relevant_state_among_moves()

    @api.multi
    def force_assign(self):
        """ Changes state of picking to available if moves are confirmed or waiting.
        @return: True
        """
        self.mapped('move_lines').filtered(lambda move: move.state in [
            'confirmed', 'waiting', 'partially_available'])._force_assign()
        return True
