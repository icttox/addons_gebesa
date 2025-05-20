# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCountryRoute(models.Model):
    _name = 'res.country.route'
    _description = 'Routes for sales order classification'

    name = fields.Text(string="Name")
