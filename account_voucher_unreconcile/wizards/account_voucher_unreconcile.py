# -*- coding: utf-8 -*-
# Copyright 2020, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class AccountVoucherUnreconcile(models.TransientModel):
    _name = 'account.voucher.unreconcile'
    _description = 'descripcion pendiente'

    payment_id = fields.Many2one(
        'account.payment',
        string='Payment',
    )

    voucher_id = fields.Many2one(
        'account.voucher',
        string='Voucher',
    )

    @api.multi
    def voucher_unreconcile_payment(self):
        _logger.warning(
            _('Entrando al metodo con valores write'))

        voucher_id = self.env['account.voucher'].browse(
            self._context.get('params', []).get('id', False))

        ctx = dict(self._context, default_voucher_id=voucher_id.id)

        aml_payment = self.env['account.move.line'].search(
            [('payment_id', '=', self.payment_id.id),
             ('account_id', '=', voucher_id.account_id.id)])

        _logger.warning(
            _('aml_payment %s'), aml_payment)

        aml_payment.with_context(ctx).remove_move_voucher_reconcile()

        _logger.warning(
            _('context %s'), self._context)
