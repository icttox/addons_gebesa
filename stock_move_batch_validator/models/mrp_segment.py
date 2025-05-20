# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpSegment(models.Model):
    _inherit = 'mrp.segment'

    schedule_all_processes = fields.Boolean(
        string='Schedule all processes',
        default=False,
        track_visibility='always',
    )

    @api.multi
    def toggle_schedule_all_processes(self):
        """ Inverse the value of the field ``schedule_all_processes``
        on the records in ``self``. """
        for record in self:
            record.schedule_all_processes = not record.schedule_all_processes

    @api.model
    def validate_schedule_all_processes(self):
        segments = self.search([
            ('state', '=', 'confirm'),
            ('schedule_all_processes', '=', True)], order="id")
        segments.production_all_processes()

    @api.multi
    def production_all_processes(self):
        for segment in self:
            productions = segment.line_ids.filtered(
                lambda lin: lin.mrp_production_id.state not in (
                    'draft', 'cancel', 'transfer')).mapped('mrp_production_id')
            productions.action_all_processes()

            done = True
            for produ in segment.line_ids.filtered(
                    lambda lin: lin.mrp_production_id.state != 'cancel'):
                if produ.manufacture_qty > 0:
                    done = False
                produ.quantity = 0
            if done:
                self.env.cr.execute(
                    "update mrp_segment set state = 'done' where id = %s",
                    (segment.id,))
