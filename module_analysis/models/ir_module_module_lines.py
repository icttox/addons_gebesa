# Copyright 2023, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class IrModuleModuleLines(models.Model):
    _name = 'ir.module.module.lines'
    _description = 'descripcion pendiente'
    _rec_name = 'module_id'

    description = fields.Text(
        string='Description',
    )

    module_id = fields.Many2one(
        'ir.module.module',
        string='Module',
        required=True,
    )

    @api.constrains('description')
    def _check_unique_description(self):
        for record in self:
            if record.description and self.search_count([('module_id', '=', record.module_id.id)]) > 1:
                raise ValidationError("Only one description is allowed per module %s" %(record.module_id.name))
