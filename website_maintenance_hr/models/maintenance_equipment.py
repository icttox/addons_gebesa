# Copyright 2023, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    def get_equipment_from_location(self, location_id):

        maintenance_team = self.env['maintenance.team'].sudo().search([('website_published', '=', True)])

        dict_equipment = []

        equipments = self.search([
            ('maintenance_team_id', 'in', maintenance_team.ids),
            ('location_physical', '=', location_id)])

        for equipment in equipments.with_context(lang='es_MX'):
            dict_equipment.append({'id': equipment.id, 'name': equipment.name})

        return dict_equipment
