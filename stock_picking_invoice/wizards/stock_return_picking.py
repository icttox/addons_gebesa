# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    invoice_state = fields.Selection(
        [('2binvoiced', 'To be refunded/invoiced'),
         ('none', 'No invoicing')],
        string="Invoicing",
        default='2binvoiced',
    )

    @api.model
    def default_get(self, fields):
        picking_obj = self.env['stock.picking']

        res = super().default_get(fields)

        record_id = self._context.get('active_ids')
        for picking in picking_obj.browse(record_id):
            if 'invoice_state' in fields:
                if picking.invoice_state == 'invoiced':
                    res['invoice_state'] = '2binvoiced'
                else:
                    res['invoice_state'] = 'none'

        return res

    @api.multi
    def _create_returns(self):
        picking_obj = self.env['stock.picking']
        bom_obj = self.env['mrp.bom']
        data = self[0]

        for line in data.product_return_moves:
            if line.to_refund:
                order_line = line.move_id.sale_line_id
                bom = bom_obj.search([(
                    'product_id', '=', order_line.product_id.id)])
                if bom and bom.type == 'phantom':
                    raise UserError(_(
                        "Cannot create a refund invoice for a kit.\n \
                        Please, uncheck the option To Refund,\n For \
                        the product %s") % order_line.product_id.name_template)

        new_picking, picking_type_id = super()._create_returns()

        if data.invoice_state == '2binvoiced':
            for move_line in picking_obj.browse(new_picking).move_ids_without_package:
                move_line.invoice_state = '2binvoiced'

        return new_picking, picking_type_id
