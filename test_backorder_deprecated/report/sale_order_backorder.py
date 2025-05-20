# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
# from odoo.exceptions import UserError


class SaleOrderBackorder(models.Model):
    _name = "sale.order.backorder"
    _description = "Sales Orders Backorder Test"
    _order = ''
    _rec_name = ''

    order_id = fields.Many2one(
        'sale.order',
        string=_('Sale Order'))

    product_family_met_id = fields.Many2one(
        'product.family',
        string=_('Product Family Metal'),
    )

    product_family_cha_id = fields.Many2one(
        'product.family',
        string=_('Product Family Veneer'),
    )

    product_family_mam_id = fields.Many2one(
        'product.family',
        string=_('Product Family Frame'),
    )

    product_family_sill_id = fields.Many2one(
        'product.family',
        string=_('Product Family Seating'),
    )

    product_family_lam_id = fields.Many2one(
        'product.family',
        string=_('Product Family Laminates'),
    )

    product_family_cdh_id = fields.Many2one(
        'product.family',
        string=_('Product Family Toolboxes'),
    )

    metal_total = fields.Float(
        string=_('Total Metal'),
    )

    veneer_total = fields.Float(
        string=_('Total Veneer'),
    )

    frame_total = fields.Float(
        string=_('Total Frame'),
    )

    seating_total = fields.Float(
        string=_('Total Seating'),
    )

    laminate_total = fields.Float(
        string=_('Total Laminates'),
    )

    toolbox_total = fields.Float(
        string=_('Total Toolboxes'),
    )
