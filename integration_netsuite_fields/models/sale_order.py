# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    ns_internal_id = fields.Char(
        string='Internal ID in Netsuite',
    )

    total_nste = fields.Float(
        string='Total Netsuite',
        digits=dp.get_precision('Account'),
        help='Total order in NetSuite',
    )

    date_netsuite = fields.Char(
        string='NetSuite capture date',
        index=True,
    )

    ok_etl = fields.Boolean(
        string='OK ETL',
        index=False,
    )
