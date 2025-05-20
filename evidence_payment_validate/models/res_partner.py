# -*- coding: utf-8 -*-
# Copyright 2019, Samuel Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    requires_evidence = fields.Boolean(
        string='Requiere Evidencias',
    )
