# -*- coding: utf-8 -*-

from odoo import models, fields


class GitUser(models.Model):
    _inherit = "project.git.user"

    odoo_user = fields.Many2one(
        'res.users',
        string="Odoo User",
    )
