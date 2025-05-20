# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProjectTaskStageHist(models.Model):
    _name = 'project.task.stage.hist'
    _order = 'date desc'
    _description = 'descripcion pendiente'

    task_id = fields.Many2one(
        'project.task',
        string=('State Task')
    )

    status_old = fields.Char(
        string=("Last Status")
    )
    status_new = fields.Char(
        string=("New Status")
    )
    date = fields.Date(
        string=("Date")
    )

    user_old = fields.Char(
        string=("Last User")
    )

    user_new = fields.Char(
        string=("New User")
    )
