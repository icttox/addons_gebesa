# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductCategoryCompanyGeb(models.Model):
    _name = 'product.category.company.geb'
    _rec_name = 'Nombre'
    _description = 'descripcion pendiente'

    Clave = fields.Char(
        string='Clave',
        copy=False,
    )

    Nombre = fields.Char(
        string='Nombre',
        copy=False,
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'product.category.company.geb')
    )
