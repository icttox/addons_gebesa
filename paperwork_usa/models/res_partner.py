# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    header_html = fields.Html(
        string='Header HTML'
    )

    footer_html = fields.Html(
        string='Footer HTML'
    )

    extra_body_html = fields.Html(
        string='Extra Body HTML',
    )

    @api.model
    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)
        res.update({
            'lang': self.env.user.company_id.partner_id.lang or self.env.lang
        })
        return res
