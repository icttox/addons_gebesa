import numpy as np

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class MrpEco(models.Model):
    _inherit = 'mrp.eco'

    @api.multi
    def _get_type_selection(self):
        res = super()._get_type_selection()
        res += [('plano', 'Plano'), ('plano_bom', 'Plano y BoM')]
        return res

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        domain="[('product_tmpl_id', '=', product_tmpl_id)]"
    )

    bom_id = fields.Many2one(
        'mrp.bom',
        domain="[('product_id', '=', product_id)]"
    )

    type = fields.Selection(
        selection=_get_type_selection,
        string='Apply on',
        default='product',
        required=True
    )

    bom_user_change_ids = fields.One2many(
        'mrp.eco.bom.change.user', 'eco_id',
        string="Manual ECO BoM Changes",
        help='Required changes in the BoM',
        states={'done': [('readonly', True)]}
    )

    @api.multi
    def action_new_revision(self):
        self.write({'state': 'progress'})

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        self.product_id = False
        self.bom_id = False

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id.variant_bom_ids:
            self.bom_id = self.product_id.variant_bom_ids.ids[0]

    @api.model
    def create(self, vals):
        eco = super().create(vals)
        if eco.type in ('bom', 'both', 'plano_bom'):
            lines_eco = eco.bom_user_change_ids.filtered(lambda r: r.change_type in ['remove', 'update'])
            list_com = np.setdiff1d(lines_eco.mapped('product_id.id'), eco.bom_id.bom_line_ids.mapped('product_id.id'))
            int_list_com = list_com.astype(int).tolist()
            list_name = self.env['product.product'].browse(int_list_com).mapped('default_code')
            if list_name:
                raise ValidationError(('Los siguientes productos de la línea de cambios de BOM no están en la lista de materiales seleccionada: %s') % list_name)
        return eco


class MrpEcoBomChangeUser(models.Model):
    _name = 'mrp.eco.bom.change.user'
    _description = 'Manual ECO BoM changes'

    eco_id = fields.Many2one('mrp.eco', 'Engineering Change', ondelete='cascade')
    eco_rebase_id = fields.Many2one('mrp.eco', 'ECO Rebase', ondelete='cascade')
    change_type = fields.Selection([
        ('add', 'Add'),
        ('remove', 'Remove'),
        ('update', 'Update')], string='Type', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    new_uom_id = fields.Many2one('uom.uom', 'New Product UoM')
    new_product_qty = fields.Float('New revision quantity', default=0)
    new_operation_id = fields.Many2one('mrp.routing.workcenter', 'New Consumed in Operation')
    # rebase_id = fields.Many2one('mrp.eco', 'Rebase', ondelete='cascade')
    # old_uom_id = fields.Many2one('uom.uom', 'Previous Product UoM')
    # old_product_qty = fields.Float('Previous revision quantity', default=0)
    # old_operation_id = fields.Many2one('mrp.routing.workcenter', 'Previous Consumed in Operation')
    # upd_product_qty = fields.Float('Quantity', compute='_compute_change', store=True)
    # uom_change = fields.Char('Unit of Measure', compute='_compute_change')
    # operation_change = fields.Char(compute='_compute_change', string='Consumed in Operation')
    # conflict = fields.Boolean()
