# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def send_not_necessary(self):
        self.env.cr.execute("""UPDATE purchase_order SET state = 'cancel'
                                    WHERE id = %s """ % (self.id))
        message_body = "<b>%s:</b> <a href=web#id=%s&view_type=form&model=purchase.order>%s</a>" % \
                        (_("El siguiente producto ya esta cancelado"), self.id, self.state)
        self.message_post(body=message_body)

    @api.multi
    def action_rfq_send(self):
        for order in self:
            if not order.partner_id.email:
                raise UserError('El Proveedor no tiene un correo electrónico capturado')

        return super().action_rfq_send()
