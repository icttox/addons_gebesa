# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def button_validate(self):
        for pick in self:
            if pick.location_dest_id.usage != 'customer':
                continue
            if not pick.sale_id:
                continue
            if pick.sale_id.not_be_billed:
                raise UserError(
                    _('This Sales Order is not invoiced'))
        return super().button_validate()

    @api.model
    def _prepare_extra_move_vals(self, qty):
        raise UserError(
            _('Favor de contactar al admistador del sistema. \n \
                Esta tansferencia creara movimientos extras'))
        # return super()._prepare_extra_move_vals(qty)
