# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpBomDetailHistory(models.Model):
    _name = 'mrp.bom.detail.history'
    _description = 'Mrp Bom Detail History'

    product_master_id = fields.Many2one(
        'product.product',
        string='Product Master',
    )
    prev_product_detail_id = fields.Many2one(
        'product.product',
        string='Previous product detail',
    )
    upd_product_detail_id = fields.Many2one(
        'product.product',
        string='Updated product detail',
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
    )
    action = fields.Selection(
        [('create', 'Create'),
         ('update', 'Update'),
         ('delete', 'Delete')],
        string="Action",
    )
    action_date = fields.Datetime(
        string="Date",
    )
    prev_qty = fields.Float(
        'Previous quantity',
    )
    upd_qty = fields.Float(
        'Updated quantity',
    )
    prev_cost = fields.Float(
        'Previous cost',
    )
    upd_cost = fields.Float(
        'Updated cost',
    )
    deference = fields.Float(
        'Deference',
    )
    id_bom = fields.Integer(
        string='Bom',
    )
    bom_id = fields.Many2one(
        'mrp.bom',
        string='BOM',
        compute='bom_id_compute'
    )
    id_bom_line = fields.Integer(
        string='Bom line',
    )
    bom_line_id = fields.Many2one(
        'mrp.bom.line',
        string='BOM Line',
        compute='bom_id_compute'
    )

    def bom_id_compute(self):
        for det in self:
            bom_id = self.env['mrp.bom'].search(
                [('id', '=', det.id_bom)])
            bom_line_id = self.env['mrp.bom.line'].search(
                [('id', '=', det.id_bom_line)])
            if bom_id:
                det.bom_id = bom_id.id
            if bom_line_id:
                det.bom_line_id = bom_line_id.id
