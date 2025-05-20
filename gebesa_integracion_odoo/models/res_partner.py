# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    inter_odoo_user = fields.Char(
        string='User odoo',
    )

    inter_odoo_pass = fields.Char(
        string='Password odoo',
    )
