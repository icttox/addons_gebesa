# Copyright 2020, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockPickingMakeBatch(models.TransientModel):
    _name = 'stock.picking.make.batch'
    _description = 'Batch Transfer Lines'

    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        check_company=True,
        default=lambda self: self.env.user,
        help='Person responsible for this batch transfer'
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,
        readonly=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'stock.picking.make.batch')
    )

    def link_pickings(self):
        # use active_ids to add picking line to the selected batch
        self.ensure_one()
        batch = self.env['stock.picking.batch'].create(
            {
                'company_id': self.company_id.id
            }
        )

        picking_ids = self.env.context.get('active_ids')
        self.env['stock.picking'].browse(picking_ids).write(
            {'batch_id': batch.id})
        batch.confirm_picking()

        return {
            'name': 'Picking batch',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.picking.batch',
            'res_id': batch.id,
        }
