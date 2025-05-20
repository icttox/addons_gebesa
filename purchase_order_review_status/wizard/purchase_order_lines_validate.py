# -*- coding: utf-8 -*-
from odoo import models, api


class PurchaseOrderLineConfirm(models.TransientModel):
    """
    This wizard will confirm the all the selected purchase order lines
    """

    _name = "purchase.order.line.confirm"
    _description = "Confirm the selected purchase order lines"

    @api.multi
    def po_lines_confirm(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['purchase.order.line'].browse(active_ids):
            if record.reviewed:
                record.reviewed = False
            else:
                record.reviewed = True
        return {'type': 'ir.actions.act_window_close'}
