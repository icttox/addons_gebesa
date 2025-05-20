# -*- coding: utf-8 -*-
# © 2021 Samuel Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    name = fields.Char(
        string='Name',
        default=lambda self: 'New',
        copy=False,
        readonly=True,
        tracking=True,
    )

    stopped_time = fields.Float(
        string='Stopped Time',
        help="Horas que permaneció detenida la máquina"
    )

    stopped_cost = fields.Float(
        string='Stopped Cost',
        help="Costo de permanecer detenida la máquina"
    )

    location_physical = fields.Many2one(
        'res.physical.location',
        related='equipment_id.location_physical',
        string='Ubicación Fisica',
    )

    attended_ids = fields.Many2many(
        'hr.employee',
        string='Attended',
    )

    memo = fields.Html(
        string='Final remarks',
    )

    complexity = fields.Selection(
        [('high', 'High'),
         ('average', 'Average'),
         ('low', 'Low')],
        string='Complexity',
    )

    accordance = fields.Selection(
        [('very_satisfied', 'Very satisfied'),
         ('satisfied', 'Satisfied'),
         ('not_satisfied', 'Not satisfied')],
        string='Accordance',
    )

    funcionality_test = fields.Boolean(
        string='Tests were carried out to ensure correct operation',
    )

    root_problem = fields.Boolean(
        string='The root problem was solved',
    )

    maintenance_attention = fields.Selection(
        [('excellent', 'Excellent'),
         ('good', 'Good'),
         ('fair', 'Fair'),
         ('bad', 'Bad')],
        string='Level of attention received by maintenance staff',
    )

    # delivery_time = fields.Selection(
    #     [('less_than_1_hr', 'Less than 1 hr'),
    #      ('day_1', 'Day 1'),
    #      ('week_1', 'Week 1'),
    #      ('more_than_1_week', 'More than 1 week')],
    #     string='Delivery time of the repaired machine or equipment',
    # )

    delivery_time = fields.Float(
        string='Delivery time of the repaired machine or equipment',
    )

    tipo_mante = fields.Selection(
        selection_add=[('migration_os', 'Migración SO'), ('enhancement', 'Mejora'), ('cctv', 'CCTV')])

    maintenance_type = fields.Selection(
        selection_add=[('migration_os', 'Migración SO'), ('enhancement', 'Mejora'), ('cctv', 'CCTV')])

    @api.model
    def create(self, vals_list):
        if vals_list.get('name', 'New') == 'New':
            vals_list['name'] = self.env['ir.sequence'].next_by_code(
                'maintenance.request.sequence')
        return super().create(vals_list)
