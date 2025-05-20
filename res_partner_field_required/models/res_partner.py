# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import ValidationError
from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    tag_footer = fields.Char(
        string='Tag footer',
    )

    @api.constrains('name')
    def _constrain_name_partner(self):
        for partner in self:
            if partner.name == '' or partner.name is False:
                raise ValidationError(_('Partner data is missing.'))

    @api.one
    def write(self, vals):
        for partner in self:
            if partner.name == '' or partner.name is False:
                raise ValidationError(_('Partner data is missing.'))
        res = super().write(vals)
        return res
