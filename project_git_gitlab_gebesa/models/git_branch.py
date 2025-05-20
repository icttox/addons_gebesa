# -*- coding: utf-8 -*-

from odoo import models, fields


class GitBranch(models.Model):
    _inherit = "project.git.branch"

    merged = fields.Boolean(
        string='Merged',
    )

    protected = fields.Boolean(
        string='Protected',
    )

    developers_can_push = fields.Boolean(
        string='Developers Can Push',
    )

    developers_can_merge = fields.Boolean(
        string='Developers Can Merge',
    )

    can_push = fields.Boolean(
        string='Can Push',
    )

    default = fields.Boolean(
        string='Default',
    )
