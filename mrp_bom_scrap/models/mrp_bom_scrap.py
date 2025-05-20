# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class MrpBomScrap(models.Model):
    _name = 'mrp.bom.scrap'
    _description = 'descripcion pendiente'

    kilos = fields.Float(
        string='Kilos',
        digits=(16, 6)
    )
    metros = fields.Float(
        string='Meters',
        digits=(16, 6)
    )
    caliber_id = fields.Many2one(
        'mrp.product.caliber',
        string='Caliber',
    )
    scrap = fields.Float(
        string='Scrap',
    )
    bom_id = fields.Many2one(
        'mrp.bom',
        string='Bom',
    )

    @api.model
    def delete_scrap(self):
        scrap_ids = self.search([('bom_id', '=', False)])
        for scrap in scrap_ids:
            scrap.unlink()
