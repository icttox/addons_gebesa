# -*- coding: utf-8 -*-
# © 2016 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class CfdiCsd(models.Model):
    _inherit = 'cfdi.csd'

    content_pem = fields.Char(
        compute='_compute_content_pem', store=True,
        help='Return the content in pem file.')
