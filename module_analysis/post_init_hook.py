# Copyright 2023, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, SUPERUSER_ID


def analyse_installed_modules(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        installed_modules = env['ir.module.module'].search(
            [('state', '=', 'installed')])
        installed_modules.button_analyse_code()
