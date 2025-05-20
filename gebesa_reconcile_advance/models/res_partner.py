# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_supplier_advance_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string=_('Account Supplier Advance'),
        # domain=[('internal_type', '=', 'receivable')],
        help=_('This account will be used for advance payment of Suppliers'),
    )

    property_account_customer_advance_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string=_('Account Customer Advance'),
        # domain=[('internal_type', '=', 'payable')],
        help=_('This account will be used for advance payment of Customers'),
    )
