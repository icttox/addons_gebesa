# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import clean_context


class ProductReplenish(models.TransientModel):
    _inherit = 'product.replenish'

    location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
    )

    def launch_replenishment(self):
        uom_reference = self.product_id.uom_id
        self.quantity = self.product_uom_id._compute_quantity(self.quantity, uom_reference)
        ctx = clean_context(self.env.context)
        ctx['replenishment_manual'] = True
        try:
            self.env['procurement.group'].with_context(ctx).run(
                self.product_id,
                self.quantity,
                uom_reference,
                # Location
                self.location_id,
                # Name
                "Manual Replenishment",
                # Origin
                "Manual Replenishment",
                # Values
                self._prepare_run_values()
            )
        except UserError as error:
            raise UserError(error)

    def _prepare_run_values(self):
        replenishment = self.env['procurement.group'].create({
            'partner_id': self.product_id.responsible_id.sudo().partner_id.id,
        })

        values = {
            'warehouse_id': self.warehouse_id,
            'route_ids': self.route_ids,
            'date_planned': self.date_planned or fields.Datetime.now(),
            'group_id': replenishment,
        }
        return values
