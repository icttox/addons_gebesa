# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class QualityAlert(models.Model):
    _inherit = 'quality.alert'

    sale_id = fields.Many2one(
        'sale.order',
        string='Sale order',
    )
    qty_reviewed = fields.Float(
        string='Quantity reviewed',
    )
    qty_rejected = fields.Float(
        string='Quantity rejected',
    )
    flaw_id = fields.Many2one(
        'quality.alert.flaw',
        string='Flaw',
    )
    provision = fields.Selection(
        [('repair', 'Repair'),
         ('scrap', 'Scrap'),
         ('released', 'Liberado')],
        string='Procision',
    )
    oven = fields.Char(
        string='Oven',
    )
    color = fields.Char(
        string='Color',
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.today,
    )
