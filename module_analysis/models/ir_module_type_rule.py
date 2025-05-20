# Copyright 2023, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class IrModuleType(models.Model):
    _name = 'ir.module.type.rule'
    _description = 'Modules Types Rules'
    _order = 'sequence'

    sequence = fields.Integer(string='Sequence')

    module_domain = fields.Char(
        string='Module Domain', required=True, default='[]')

    module_type_id = fields.Many2one(
        string='Module type', comodel_name='ir.module.type', required=True)

    @api.multi
    def _get_module_type_id_from_module(self, module):
        ir_module_module = self.env['ir.module.module']
        for rule in self:
            domain = safe_eval(rule.module_domain)
            domain.append(('id', '=', module.id))
            if ir_module_module.search(domain):
                return rule.module_type_id.id
        return False
