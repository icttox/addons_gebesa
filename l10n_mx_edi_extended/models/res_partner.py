# Copyright 2020, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import re
from odoo import fields, models


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    l10n_mx_edi_payment_method_id = fields.Many2one(
        'l10n_mx_edi.payment.method',
        string='Payment method',
    )

    l10n_mx_edi_name = fields.Char(
        string='Name to CFDI',
    )

    def _l10n_mx_edi_clean_to_legal_name(self):
        """ We remove the SA de CV / SL de CV / S de RL de CV as they are never in the official name in the XML"""
        regex = re.compile(r"(\s+(s\.?[acl]\.?|s\.? de r\.?l\.?)" r"( de c\.?v\.?|))\s*$", re.I)
        self.l10n_mx_edi_name = regex.sub("", self.name).upper()
