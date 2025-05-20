# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import api, models, fields, tools, _


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    mark = fields.Char(
        string='Mark',
    )

    capacity = fields.Char(
        string='Capacity',
    )

    dimensions = fields.Char(
        string='Dimensions',
    )

    int_number = fields.Char(
        string='Internal Number',
    )

    security_device = fields.Char(
        string='Security Device'
    )

    image = fields.Binary(
        string="Image",
        attachment=True,
    )

    image_medium = fields.Binary(
        string="Medium-sized image",
        attachment=True,
    )

    image_small = fields.Binary(
        string="Small-sized image",
        attachment=True,
    )

    parent_id = fields.Many2one(
        'maintenance.equipment',
        string="Parent",
    )

    component_ids = fields.One2many(
        'maintenance.equipment',
        'parent_id',
        string="Component"
    )

    last_ip = fields.Char(
        string="Last IP"
    )

    it_software_equipment_rel_ids = fields.One2many(
        'it.software.equipment.rel',
        'equipment_id',
        string='IT Softare Equipment Rel',
    )

    ficha_tecnica = fields.Html(
        string='Ficha tecnica',
    )

    image_render = fields.Binary(
        string='Imagen render',
        attachment=True,
    )

    image_plano = fields.Binary(
        string='Imagen plano',
        attachment=True,
    )

    status_validation = fields.Selection(
        [('external_calibration', 'External calibration'),
         ('compliant_verification', 'Compliant verification'),
         ('loss_replacement', 'Loss replacement'),
         ('replacement_destruction', 'Destruction Replacement'),
         ('new_compliant_verification', 'New compliant verification'),
         ('replenishment_non_compliance', 'Replenishment non compliance'),
         ('internal_verification', 'Internal verification')],
        string='Status validation',
    )

    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
    )

    replacement = fields.Boolean(
        string='replacement',
    )

    maintenance_activities = fields.Text(
        string='Actividades mantenimiento',
    )

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals=vals, big_name='image',
                                  medium_name='image_medium',
                                  small_name='image_small')
        return super(MaintenanceEquipment, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals=vals, big_name='image',
                                  medium_name='image_medium',
                                  small_name='image_small')
        return super(MaintenanceEquipment, self).write(vals)

    def _create_new_request(self, date):
        self.ensure_one()
        self.env['maintenance.request'].create({
            'name': _('Preventive Maintenance - %s') % self.name,
            'request_date': date,
            'schedule_date': date + timedelta(days=10),
            'category_id': self.category_id.id,
            'equipment_id': self.id,
            'maintenance_type': 'preventive',
            'owner_user_id': self.owner_user_id.id,
            'user_id': self.technician_user_id.id,
            'maintenance_team_id': self.maintenance_team_id.id,
            'duration': self.maintenance_duration,
            'company_id': self.company_id.id,
        })
