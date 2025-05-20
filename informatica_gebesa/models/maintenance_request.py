# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    tipo_mante = fields.Selection(
        [('preventive', 'Preventive'),
         ('corrective', 'Corrective'),
         ('Predictive', 'Predictive')],
        string='Type of Maintenance'
    )

    garantia = fields.Boolean(
        string='Warranty',
    )

    technical_description = fields.Text(
        string='Technical Description',
    )

    maintenance_type = fields.Selection(
        selection_add=[('predictive', 'Predictive')])

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.equipment_id = ''
