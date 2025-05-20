# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = ['message.post.show.all', 'project.task']
