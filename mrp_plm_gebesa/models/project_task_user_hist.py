# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProjectTaskUserHist(models.Model):
    _name = 'project.task.user.hist'
    _order = 'date desc'
    _description = 'descripcion pendiente'

    task_id = fields.Many2one(
        'project.task',
        string=('State Task')
    )

    user_old = fields.Char(
        string=("Last User")
    )
    user_new = fields.Char(
        string=("New User")
    )
    date = fields.Datetime(
        string=("Date")
    )
