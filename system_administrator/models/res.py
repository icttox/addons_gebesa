# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def write(self, vals):
        if 'active' in vals and not self.env.user.has_group(
                'system_administrator.group_system_administrator_gebesa'):
            raise UserError(_('only administrator can activate/deactivate'))
        return super().write(vals)
