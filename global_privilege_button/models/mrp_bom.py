# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, _, models
from odoo.exceptions import UserError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def create(self, vals):
        if not self.env.user.has_group(
                'global_privilege_button.group_manager_ldm'):
            raise UserError(_('Error!\nYou do not have privileges to Create'
                              ' Material(s) list.\nCheck with your'
                              ' System Administrator.'))
        return super(MrpBom, self).create(vals)

    @api.one
    def write(self, vals):
        if not self.env.user.has_group(
                'global_privilege_button.group_manager_ldm'):
            raise UserError(_('Error!\nYou do not have privileges to Modify'
                              ' Material(s) list.\nCheck with your'
                              ' System Administrator.'))
        return super(MrpBom, self).write(vals)

    @api.multi
    def unlink(self):
        if not self.env.user.has_group(
                'global_privilege_button.group_manager_ldm'):
            raise UserError(_('Error!\nYou do not have privileges to Delete'
                              ' Material(s) list.\nCheck with your'
                              ' System Administrator.'))
        return super(MrpBom, self).unlink()

    @api.multi
    def toggle_active(self):
        for rec in self:
            if rec.active and rec.bom_line_ids:
                raise UserError(_('Error!\nYou can not Inactivate this BOM,'
                                  ' you need to delete all the lines.'))
        return super(MrpBom, self).toggle_active()
