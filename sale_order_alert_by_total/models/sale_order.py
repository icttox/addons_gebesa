# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import _, api, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        res = super().action_confirm()

        mail_obj = self.env['mail.mail']
        return res

        for order in self:
            if order.pricelist_id.currency_id.name == 'MXN' and \
               order.amount_total >= 200000 or \
               order.pricelist_id.currency_id.name == 'USD' and \
               order.amount_total >= 10000:
                body_mail = "<b>%s</b> \
                            <a href=web#id=%s&view_type=form&model=sale.order>%s</a> \
                            <b>%s:</b> \
                            <a href=web#id=%s&view_type=form&model=res.partner>%s</a> \
                            <b>%s %s %s.</b>" % (_('Se validó un Pedido de Venta'),
                                                 order.id, order.name,
                                                 _('del Cliente'),
                                                 order.partner_id.id,
                                                 order.partner_id.name,
                                                 _('con un Monto Total de $'),
                                                 order.amount_total,
                                                 order.pricelist_id.currency_id.name)

                mail = mail_obj.create({
                    'subject': 'Re:' + order.name,
                    'email_to': 'equipocompras@gebesa.com,sistemas@gebesa.com,sebastian@gebesa.com,programacion@gebesa.com,cristina.rodriguez@gebesa.com',
                    'headers': "{'Return-Path': u'odoo@gebesa.com'}",
                    'body_html': body_mail,
                    'auto_delete': True,
                    'message_type': 'comment',
                    'model': 'sale.order',
                    'res_id': order.id,
                })
                mail.send()

        return res
