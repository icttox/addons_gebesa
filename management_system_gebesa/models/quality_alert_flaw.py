# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class QualityAlertFlaw(models.Model):
    _name = 'quality.alert.flaw'
    _description = 'Quality Alert Defects'

    code = fields.Char(
        string='Code',
    )
    name = fields.Char(
        string='Name',
    )
    workcenter_ids = fields.Many2many(
        'mrp.workcenter',
        string='Work Centers',
    )

    @api.multi
    def name_get(self):
        return [(
            record.id, record.code + '.- ' + record.name) for record in self]
