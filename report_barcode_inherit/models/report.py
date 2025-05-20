# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from reportlab.graphics.barcode import createBarcodeDrawing


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def barcode(self, barcode_type, value,
                width=600, height=100, humanreadable=0):
        kwargs = {}
        if barcode_type == 'UPCA' and len(value) in (11, 12, 13):
            barcode_type = 'EAN13'
            if len(value) in (11, 12):
                value = '0%s' % value
        elif barcode_type == 'auto':
            symbology_guess = {8: 'EAN8', 13: 'EAN13'}
            barcode_type = symbology_guess.get(len(value), 'Code128')
        # add QR_quiet type for QR type with no border (not in 13.0 since there is quiet argument)
        if barcode_type == 'QR_quiet':
            kwargs['quiet'] = 1
            kwargs['barBorder'] = 0
            barcode_type = 'QR'
        try:
            width, height, humanreadable = int(width), int(
                height), bool(int(humanreadable))
            barcode = createBarcodeDrawing(
                barcode_type, value=value, format='png', width=width,
                height=height, humanReadable=humanreadable, checksum=0,
                **kwargs
            )
            return barcode.asString('png')
        except (ValueError, AttributeError):
            if barcode_type == 'Code128':
                raise ValueError("Cannot convert into barcode.")
            return self.barcode('Code128', value, width=width,
                                height=height, humanreadable=humanreadable,
                                checksum=0)
