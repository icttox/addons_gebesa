# -*- coding: utf-8 -*-
# © <2017> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class WizardCutDetail(models.TransientModel):
    _name = 'wizard.cut.detail'

    bom_id = fields.Many2one(
        'mrp.bom',
        string='BoM'
    )

    @api.multi
    def print_report_wizard(self):
        # import pdb; pdb.set_trace()
        ids = [self.id]
        ctx = dict(self.env.context or {},
                   active_ids=ids,
                   active_model=self._name)
        return{
            'type': 'ir.actions.report.xml',
            'report_name': 'wizard.cut.detail.report',
            'context': ctx,
        }
