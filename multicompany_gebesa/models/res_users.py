# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, SUPERUSER_ID
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if 'company_id' in vals:
            if self.id == SUPERUSER_ID:
                raise UserError('You can not change the company of this user.')
            operating_unit = self.env['operating.unit'].sudo().search(
                [('company_id', '=', vals['company_id'])],
                order='id desc', limit=1)
            if operating_unit:
                self.write({'default_operating_unit_id': operating_unit.id})
        return res
