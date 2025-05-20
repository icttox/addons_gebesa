from odoo import api, fields, models


class ProductFamilyUpdateWizard(models.TransientModel):
    _name = 'product.family.update.wizard'
    _description = 'descripcion pendiente'

    family_id = fields.Many2one(
        'product.family',
        string='Product Family',
    )

    @api.multi
    def update_family(self):
        active_ids = self._context.get('active_ids', []) or []
        self._cr.execute('UPDATE product_template '
                         'SET family_id=%s '
                         'WHERE id IN %s', (self.family_id.id, tuple(active_ids)))
