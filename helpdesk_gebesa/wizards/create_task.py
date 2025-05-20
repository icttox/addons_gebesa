# -*- coding: utf-8 -*-

from odoo import _, models, fields, api
from odoo.exceptions import ValidationError


class CreateTaskTicket(models.TransientModel):
    _name = 'create.task.ticket'
    _description = 'descripcion pendiente'

    acceptance_criterias = fields.Html(
        string='Acceptance Criterias',
        required=True
    )

    type_id = fields.Many2one(
        'project.task.type2',
        string="Type",
        required=True
    )

    priority_id = fields.Many2one(
        'project.task.priority',
        string="Priority",
        required=True
    )


    @api.multi
    def task_create(self):
        if self._context.get('active_model') != 'helpdesk.ticket':
            raise ValidationError(_("Wrong model."))
        res_id = self._context.get('active_ids')
        ticket = self.env['helpdesk.ticket'].browse(res_id[0])
        if not ticket.project_id.id:
            raise ValidationError(_("Doesnt have a project assigned."))
        if not  ticket.user_id.id:
            raise ValidationError(_("Doesnt have an assigned user."))
        task_id = self.env['project.task'].create({
                           'name': ticket.name,
                           'project_id': ticket.project_id.id,
                           'description': self.acceptance_criterias,
                           'type_id': self.type_id.id,
                           'priority_id': self.priority_id.id,
                           'user_id': ticket.user_id.id})
        ticket.task_id = task_id
        act = {
           'name': 'Tasks Created',
           'type': 'ir.actions.act_window',
           'res_model': 'project.task',
           'target': 'current',
           'view_mode': 'tree,form',
           'domain': [('id', '=', [task_id.id])]}
        return act
