# -*- coding: utf-8 -*-

from odoo import fields, models
# from odoo.addons.l10n_mx_edi.hooks import _load_xsd_files


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_mx_edi_pac = fields.Selection(
        selection_add=[('comdig', 'Comercio Digital')],
    )
