# -*- coding: utf-8 -*-
# © 2017 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductNstPlant(models.Model):
    _name = 'product.nst.plant'
    _description = 'Clase temporal mientras se tenga la integracion con NS'
    _order = "name asc"

    name = fields.Char(
        string='Name',
        size=120,
        required=True,
        help='Plant name',
    )

    nstid = fields.Integer(
        string='NetSuite Id',
    )


class ProductNstLine(models.Model):
    _name = 'product.nst.line'
    _description = 'Clase temporal mientras se tenga la integracion con NS'
    _order = "name asc"

    name = fields.Char(
        string='Name',
        size=120,
        required=True,
        help='Line name',
    )

    nstid = fields.Integer(
        string='NetSuite Id',
    )

    product_nstplant_id = fields.Many2one(
        'product.nst.plant',
        string='Product Plant',
    )


class ProductNstTipo(models.Model):
    _name = 'product.nst.tipo'
    _description = 'Clase temporal mientras se tenga la integracion con NS'
    _order = "name asc"

    name = fields.Char(
        string='Name',
        size=120,
        required=True,
        help='Type name',
    )

    nstid = fields.Integer(
        string='NetSuite Id',
    )

    product_nstline_id = fields.Many2one(
        'product.nst.line',
        string='Product Line',
    )
