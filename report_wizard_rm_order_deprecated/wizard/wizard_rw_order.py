# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class SegmentReportArmed(models.TransientModel):
    _name = 'raw.material.order.wizard'

    order_ids = fields.Many2many(
        'sale.order',
        string=_('Orders'),
    )

    @api.multi
    def print_report(self):
        ids = [self.id]
        ctx = dict(self.env.context or {},
                   active_ids=ids,
                   active_model=self._name)
        return{
            'type': 'ir.actions.report.xml',
            'report_name': 'concentrado.mp.por.pedido',
            'context': ctx,
        }
