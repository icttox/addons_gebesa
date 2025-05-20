# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, exceptions, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    notify_approval = fields.Char(
        string='Notify Sale Approval',
    )

    @api.multi
    def unlink(self):
        for rec in self:
            order = self.env['sale.order'].search([
                ('partner_shipping_id', '=', rec.id)])
            if order:
                raise exceptions.UserError(
                    "Este contacto se utiliza como direccion de entrega en al \
                    menos 1 pedido")
        return super().unlink()
