# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    @api.model
    def create(self, vals):
        if not self.env.user.has_group(
                'mrp_plm_gebesa.group_manager_project_task_type'):
            raise UserError(_('Only Administrator can create'))
        return super(ProjectTaskType, self).create(vals)

    @api.multi
    def write(self, vals):
    	# import ipdb; ipdb.set_trace()
        if not self.env.user.has_group(
                'mrp_plm_gebesa.group_manager_project_task_type'):
            raise UserError(_('Only administrator can edit'))
        return super(ProjectTaskType, self).write(vals)

    @api.multi
    def unlink(self, vals):
        if not self.env.user.has_group(
                'mrp_plm_gebesa.group_manager_project_task_type'):
            raise UserError(_('Only admin can delete'))
        return super(ProjectTaskType, self).unlink()
