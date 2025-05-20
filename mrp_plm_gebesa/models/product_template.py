# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    attachment_ids = fields.One2many(
        'ir.attachment', 'res_id',
        domain=[('res_model', '=', 'product.product')], string='Attachments')

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    consecutive_id = fields.Char(
        string='Consecutive Name'
    )

    version = fields.Integer(
        string='Version',
    )

    plm_project_id = fields.Many2one(
        'project.task',
        string='Project Task'
    )

    plm_project_related = fields.Many2one(
        'project.task',
        string='Project Task Related'
    )
    type = fields.Selection(selection_add=[('cotiza', 'Quotation')])

    attachment_ids = fields.One2many(
        'ir.attachment', 'res_id',
        domain=[('res_model', '=', 'product.template')], string='Attachments')

    _sql_constraints = [
        ('consecutive_id_uniq', 'unique (consecutive_id)',
         'This field must be unique!')
    ]

    @api.multi
    @api.onchange('type')
    def onchange_type(self,):
        for product in self:
            res = {}
            if self.type == 'cotiza':
                codigo = self.env['ir.sequence'].next_by_code('articulo') or '/'
                res = {'value': {'consecutive_id': codigo}}
            return res

    @api.multi
    def write(self, vals):
        if 'type' in vals.keys():
            for product in self:
                if vals.get('type') == 'cotiza' and product.type != 'cotiza':
                    raise ValidationError(
                        _("You cannot turn a Non quotation product into a quotation product"))

        if vals.get('default_code'):
            for product in self:
                if product.type == 'cotiza':
                    res = {'default_code': product.consecutive_id}
                    vals.update(res)
        return super(ProductTemplate, self).write(vals)

    @api.model
    def create(self, vals):
        nombre = vals.get('consecutive_id')
        tipo = vals.get('type')
        costo = False
        if vals.get('standard_price'):
            costo = float(vals.get('standard_price'))

        if vals.get('reference_mask'):
            if tipo == 'product' and (not costo or costo < 0.001):
                raise ValidationError(
                    _("Cost is required and must be at least 0.001 in stockable products, please verify..."))

        if nombre and tipo == 'cotiza':
            if vals.get('version') >= 1:
                adicional = vals.get('version')
                adicional = adicional + 1
                adicional = str(adicional)
                nombre = nombre[:10]
                vals['default_code'] = nombre + adicional
                vals['consecutive_id'] = nombre + adicional
                vals['version'] = adicional
            else:
                conca = '1'
                vals['default_code'] = nombre + 'V' + conca
                vals['consecutive_id'] = nombre + 'V' + conca
                vals['version'] = conca

        return super(ProductTemplate, self).create(vals)

    @api.multi
    def transformacion(self):
        if self.plm_project_id and self.plm_project_id.id:
            raise ValidationError(_("This product have a Project Task"))
        return {
            'name': _('Transformation'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.plm.gebesa.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': self._context,
        }
