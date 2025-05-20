# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_mx_edi_skip_waybill = fields.Boolean(
        'Need Skip Waybill?', help='Check this box to add by default '
        'the skip waybill complement in invoices for this customer.')
