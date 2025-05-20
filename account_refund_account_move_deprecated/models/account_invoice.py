# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def invoice_line_move_line_get(self):
        return_account_id = self.env[
            'ir.config_parameter'].sudo().get_param(
                'res_settings_freight.return_account_id')

        if not return_account_id:
            raise ValidationError(_(u"Please specify an account of \
                                  refund in Accounting --> \
                                  Configuration --> Settings"))

        res = super().invoice_line_move_line_get()
        for line in res:
            if self.dev_tipo == 'normal' and self.type == "out_refund":
                if line['product_id']:
                    line['account_id'] = return_account_id

        return res
