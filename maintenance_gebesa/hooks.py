# Copyright 2021 Samuel Barron
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):

    env = api.Environment(cr, SUPERUSER_ID, {})

    maintenance_obj = env["maintenance.request"]
    maintenance_ids = maintenance_obj.search([], order='id')

    for maint in maintenance_ids:
        name = env['ir.sequence'].next_by_code(
            'maintenance.request.sequence')
        maint.write({'name': name})
