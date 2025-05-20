# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class TmsWizardValidate(models.TransientModel):
    _name = 'tms.wizard.validate'
    _description = 'descripcion pendiente'

    @api.multi
    def process_all(self):
        active_model = self._context.get('active_model')
        records = self.env[active_model].browse(
            self._context.get('active_ids'))
        for record in records:
            if record.state == 'draft':
                record.action_approve()
            if record.state == 'authorized':
                record.action_authorized()
            if record.state == 'approved':
                record.action_confirm()
