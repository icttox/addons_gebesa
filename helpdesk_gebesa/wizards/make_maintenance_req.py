# -*- coding: utf-8 -*-

from odoo import _, models, fields, api
from odoo.exceptions import ValidationError


class MakeMaintenanceReq(models.TransientModel):
    _name = 'make.maintenance.req'
    _description = 'descripcion pendiente'

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        required=True
    )

    tipo = fields.Selection(
        [('preventive', 'Preventive'),
         ('corrective', 'Corrective'),
         ('Predictive', 'Predictive')],
        string='Type',
        required=True
    )

    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string="Equipo/Maquina",
        required=True
    )

    user_id = fields.Many2one(
        'res.users',
        required=True,
        string='Responsable'
    )

    @api.multi
    def request_maintenance(self):
        if self._context.get('active_model') != 'helpdesk.ticket':
            raise ValidationError(_("Wrong model."))
        res_id = self._context.get('active_ids')
        ticket = self.env['helpdesk.ticket'].browse(res_id[0])
        maintenance_id = self.env['maintenance.request'].create({
                                #   'name': ticket.name,
                                  'employee_id': self.employee_id.id,
                                  'company_id': self.env.user.company_id.id,
                                  'description': ticket.description,
                                  'equipment_id': self.equipment_id.id,
                                  'request_date': ticket.create_date,
                                  'tipo': self.tipo,
                                  'user_id': self.user_id.id})
        ticket.maintenance_id = maintenance_id
        act = {
           'name': 'Requests Maintenance Created',
           'type': 'ir.actions.act_window',
           'res_model': 'maintenance.request',
           'target': 'current',
           'view_mode': 'tree,form',
           'domain': [('id', 'in', [maintenance_id.id])]}
        return act
