# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpPlmGebesaWizard(models.TransientModel):
    _name = 'mrp.plm.gebesa.wizard'
    _description = 'descripcion pendiente'

    user_id = fields.Many2one(
        'res.users',
        required=True,
        string='Assigned',
    )

    order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
    )

    muestra = fields.Boolean(
        string='Sample',
    )

    clave = fields.Boolean(
        string='Key',
    )

    costo = fields.Boolean(
        string='Cost',
    )

    planted = fields.Boolean(
        string='Planted',
    )

    render = fields.Boolean(
        string='Render',
    )

    planos = fields.Boolean(
        string='Planes',
    )

    description = fields.Html(
        'Description',
        required=True
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer')

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse')

    project_id = fields.Many2one(
        'project.project',
        required=True,
        string='Project'
    )

    date_deadline = fields.Datetime(
        string='Fecha limite',
    )

    is_special = fields.Boolean(
        string='Esta tarea contendra productos de tipo especial',
    )

    @api.multi
    def transformation_user(self):

        res_id = self._context.get('active_ids')
        project_obj = self.env['project.task']
        product_obj = self.env['product.template']
        muestra_wizard = False
        clave_wizard = False
        costo_wizard = False
        planted_wizard = False
        render_wizard = False
        planos_wizard = False
        special_wizard = False
        for a in res_id:
            product_var = product_obj.search([('id', '=', a)])

        # if not product_var.description_sale:
        #     raise UserError(_('You need to specify a description in tab Notes --> Description Sale'))

        if self.muestra:
            muestra_wizard = self.muestra
        if self.clave:
            clave_wizard = self.clave
        if self.costo:
            costo_wizard = self.costo
        if self.planted:
            planted_wizard = self.planted
        if self.render:
            render_wizard = self.render
        if self.planos:
            planos_wizard = self.planos
        if self.is_special:
            special_wizard = self.is_special

        idd = project_obj.create({'sequence': 1,
                                  'name': product_var.consecutive_id,
                                  'kanban_state': 'normal',
                                  'date_deadline': self.date_deadline,
                                  'product_id': product_var.id,
                                  'description': self.description,
                                  'partner_id': self.partner_id.id,
                                  'order_id': self.order_id.id,
                                  'muestra': muestra_wizard,
                                  'warehouse_id': self.warehouse_id.id,
                                  'project_id': self.project_id.id,
                                  'clave': clave_wizard,
                                  'costo': costo_wizard,
                                  'planted': planted_wizard,
                                  'render': render_wizard,
                                  'planos': planos_wizard,
                                  'user_id': self.user_id.id,
                                  'is_special': special_wizard})
        product_var.plm_project_id = idd
        idd.user_id = self.user_id.id
        idd.description = self.description
        product_var.type = 'product'
        return True
