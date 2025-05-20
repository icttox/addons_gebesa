# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class PedidosVinculados(models.Model):
    _name = 'pedidos.vinculados'
    _rec_name = 'folio'
    _description = 'descripcion pendiente'

    folio = fields.Char(
        string='Folio'
    )

    fecha = fields.Date(
        string='Date',
        default=fields.Date.today
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner'
    )

    activo = fields.Boolean(
        string='Active',
        default=True
    )

    description = fields.Text(
        string='Description',
    )

    order_ids = fields.Many2many(
        'sale.order',
        string='Orders'
    )

    # @api.model
    # def check_order(self, vals):
    #    import pdb; pdb.set_trace()
    #    for i in self:
    #        for vin in len(i.order_ids):
                # for order in self:
    #            if vin < 2:
    #                raise UserError(_('You can not delete this segment'))
                # order_obj = self.env['sale.order']
                # o = order_obj.search[()]
                # if order.pedidos_vinculados_bool:
                #    raise UserError(_('You can not delete this segment'))

    # @api.model
    # def create(self, vals):
    #    import pdb; pdb.set_trace()
    #    if len(self.order_ids) < 2:
    #        raise UserError(_('You can not delete this segment'))
    #    if vals.get()
    #    order_obj = self.env['sale.order']
    #    order = order_obj.search([('id', '=', order_ids.id)])
            # for order in vin.order_ids:
            #    order.pedidos_vinculados_bool = True
        # return True

    # @api.multi
    # def write(self, vals):
    #	import pdb; pdb.set_trace()
    #    if len(self.order_ids) < 2:
     #       raise UserError(_('You can not delete this segment'))
    #    if vals.get()
# class SaleOrder(models.Model):
#    _inherit = 'sale.order'

#    pedidos_vinculados_bool = fields.Boolean(
#        string=_('Linked Orders'),
#    )
