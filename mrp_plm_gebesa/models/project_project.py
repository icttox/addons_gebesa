# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import models

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = 'project.project'
    _order = 'name desc'
