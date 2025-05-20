# -*- coding: utf-8 -*-

from odoo import _, models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import html2plaintext


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    maintenance_id = fields.Many2one(
        'maintenance.request',
        string='Maintenance Request'
    )

    task_id = fields.Many2one(
        'project.task',
        string='Project Task'
    )

    @api.multi
    def create_request_maintenance(self):
        if self.maintenance_id and self.maintenance_id.id:
            raise ValidationError(_("This maintenance request has already been assigned."))
        return {
            'name': _('Create Maintenance Req'),
            'type': 'ir.actions.act_window',
            'res_model': 'make.maintenance.req',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': self._context,
        }

    @api.multi
    def create_request_task(self):
        if self.task_id and self.task_id.id:
            raise ValidationError(_("This task has already been assigned."))
        return {
            'name': _('Create Task'),
            'type': 'ir.actions.act_window',
            'res_model': 'create.task.ticket',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': self._context,
        }

    @api.model
    def message_new(self, msg, custom_values=None):
        ticket = super(HelpdeskTicket, self).message_new(msg, custom_values=custom_values)
        body = msg.get('body')
        body = html2plaintext(body) if body else ''
        ticket.description = body
        return ticket

    @api.onchange('partner_id', 'project_id')
    def _onchange_partner_project(self):
        if self.project_id:
            domain = [('project_id', '=', self.project_id.id)]
            if self.partner_id:
                domain.extend(['|',
                               ('partner_id', 'child_of', self.partner_id.commercial_partner_id.id),
                               ('partner_id', '=', False),
                               ])
            # Take the latest task and set it.
            # self.task_id = self.env['project.task'].search(domain, limit=1)
            return {'domain': {'task_id': domain}}

    @api.multi
    def get_url_assign_me(self):
        return self._notify_get_action_link('assign')
