# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    website_published = fields.Boolean(string="Publish on website")

    @api.multi
    def website_publish_button(self):
        self.ensure_one()
        return self.write({'website_published': not self.website_published})
