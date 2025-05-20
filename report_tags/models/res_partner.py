# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    template_label = fields.Selection(
        [('1', 'Template 1 (Generico)'),
         ('2', 'Template 2 (Metalia)'),
         ('3', 'Template 3 (Clear Design)'),
         ('4', 'Template 4 (Caterpillar)'),
         ('5', 'Template 5 (ULOFT)'),
         ('6', 'Template 6 (Doane Keyes)'),
         ('7', 'Template 7 (Global Industrial)')],
        string='Type Of Label',
        default='1'
    )

    type_barcode = fields.Selection(
        [('CCode39', 'CCode39'),
         ('Code128bWin', 'Code128bWin'),
         ('UPC_A', 'UPC-A')],
        string='Type Of Barcode',
        default='CCode39'
    )
    vendor_code = fields.Char(
        string='Vendor code',
    )
