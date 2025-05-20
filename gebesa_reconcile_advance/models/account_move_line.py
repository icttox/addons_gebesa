# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None,
                count=False, access_rights_uid=None):

        move_obj = self.pool.get('account.move.line')
        payment_obj = self.pool.get('account.payment')
        context = self._context

        lista_invoice = context.get('has_invoice_ids', False)
        lista_invoice = lista_invoice and lista_invoice[0] or []
        lista_invoice = lista_invoice and lista_invoice[2] or []

        lista_payment = context.get('has_payment_ids', False)
        lista_payment = lista_payment and lista_payment[0] or []
        lista_payment = lista_payment and lista_payment[2] or []

        no_incluir = ['id', 'not in', []]
        l_ids = []

        if lista_invoice:
            context.pop('has_invoice_ids')
            for inv in lista_invoice:
                moves_up = move_obj.search([('invoice', '=', inv)])
                l_ids = l_ids + moves_up

        if lista_payment:
            context.pop('has_payment_ids')
            for pay in lista_payment:
                payments_up = payment_obj.browse(pay)
                mv = payments_up.move_id.id
                moves_up = move_obj.search([('move_id', '=', mv)])
                l_ids = l_ids + moves_up

        if l_ids != []:
            no_incluir[2] += l_ids

            args.append(no_incluir)

        return super()._search(
            args=args, offset=offset, limit=limit, order=order,
            count=count, access_rights_uid=access_rights_uid)
