# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    omitir_rt = fields.Boolean(
        string='Omitir Facturas de RT',
        default=False
    )

    custom_broker = fields.Boolean(
        string='Agente Aduanal',
    )

    transporter = fields.Boolean(
        string='Trasportista',
    )
