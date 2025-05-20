# Copyright 2023, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class BaseModuleUpdate(models.TransientModel):
    _inherit = 'base.module.update'
    _description = 'descripcion pendiente'

    analyse_installed_modules = fields.Boolean(
        string='Analyse Installed Modules', default=True)

    @api.multi
    def update_module(self):
        return super(BaseModuleUpdate, self.with_context(
            analyse_installed_modules=self.analyse_installed_modules)
        ).update_module()
