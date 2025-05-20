# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    id_ns = fields.Integer(
        'ID Netsuite',
    )

    id_dir_ns = fields.Integer(
        'ID Address Netsuite',
    )
