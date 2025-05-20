# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class SegmentReportArmed(models.TransientModel):
    _name = 'segment.send.armed.wizard'

    segment_ids = fields.Many2many(
        'mrp.segment',
        string=_('Select Segments'),)

    @api.multi
    def print_report(self):
        ids = [self.id]
        ctx = dict(self.env.context or {},
                   active_ids=ids,
                   active_model=self._name)
        return{
            'type': 'ir.actions.report.xml',
            'report_name': 'segment.armed.report',
            'context': ctx,
        }

    @api.multi
    def print_report_mp_concentrado(self):
        ids = [self.id]
        ctx = dict(self.env.context or {},
                   active_ids=ids,
                   active_model=self._name)
        return{
            'type': 'ir.actions.report.xml',
            'report_name': 'exportacion.mp.concentrado.wizard',
            'context': ctx,
        }

    @api.multi
    def print_report_order_wood(self):
        ids = [self.id]
        ctx = dict(self.env.context or {},
                   active_ids=ids,
                   active_model=self._name)
        return{
            'type': 'ir.actions.report.xml',
            'report_name': 'cut.order.wood.wizard',
            'context': ctx,
        }

    @api.multi
    def export_for_optimizer(self):
        ids = [self.id]
        ctx = dict(self.env.context or {},
                   active_ids=ids,
                   active_model=self._name)
        return{
            'type': 'ir.actions.report.xml',
            'report_name': 'cut.order.wood.wizard.optimizador',
            'context': ctx,
        }
