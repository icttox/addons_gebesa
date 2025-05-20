# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from odoo import fields, models, api


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    consecutive_id = fields.Char(
        string='Code'
    )
    nuevo = fields.Boolean(
        string='Nuevo',
        default=False,
    )
    employee_log_ids = fields.One2many(
        'maintenance.equipment.employee.log',
        'equipment_id',
        string='employee_log_ids',
    )
    fecha_vencimiento = fields.Date(
        string=('Fecha Vencimiento'),
        copy=False)
    dias_restantes = fields.Integer(
        compute='_compute_insurance_days_to_expire_date',
        string='Dias Restantes')

    location_physical = fields.Many2one(
        'res.physical.location',
        string='Ubicacion Fisica',
    )

    _sql_constraints = [
        ('consecutive_id_uniq', 'unique (consecutive_id)',
         'This field must be unique!')
    ]

    @api.model
    def create(self, vals):
        vals['consecutive_id'] = self.env['ir.sequence'].next_by_code('equipo') or '/'
        return super(MaintenanceEquipment, self).create(vals)

    @api.depends('fecha_vencimiento')
    def _compute_insurance_days_to_expire_date(self):
        for rec in self:
            if self.fecha_vencimiento != 0:
                now = datetime.now().date()
                date_expire = rec.fecha_vencimiento if rec.fecha_vencimiento else datetime.now().date()
                delta = date_expire - now
                if delta.days >= -1:
                    rec.dias_restantes = delta.days + 1
                else:
                    rec.dias_restantes = 0
