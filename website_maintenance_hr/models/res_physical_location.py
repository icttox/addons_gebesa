# Copyright 2023, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ResPhysicalLocation(models.Model):
    _inherit = 'res.physical.location'

    website_published = fields.Boolean(string="Publish on website")

    @api.multi
    def website_publish_button(self):
        self.ensure_one()
        return self.write({'website_published': not self.website_published})
