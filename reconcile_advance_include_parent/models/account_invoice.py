# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        res = {}
        res2 = {}
        res = super().search(args, offset, limit, order, count=count)
        partner_obj = self.env['res.partner']

        if context and context.get('include_padre', True) and 'partner_id' in context:
            partner_id = context.get('partner_id')
            for main_partner in partner_obj.browse([partner_id]):
                res2 = []
                for child_partner in main_partner.child_ids:
                    new_args = []
                    for argument in args:
                        if 'partner_id' in argument:
                            partner_arg = ['partner_id', '=', child_partner.id]
                            new_args.append(partner_arg)
                        else:
                            new_args.append(argument)

                    res2 = super().search(new_args, offset, limit, order, count=count)
                    res += res2
        return res
