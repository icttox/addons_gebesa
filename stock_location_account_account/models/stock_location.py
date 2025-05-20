# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    account_id = fields.Many2one(
        'account.account',
        string='Inventory account',
    )

    @api.model
    def _location_owner(self, location):
        ''' Return the company owning the location if any '''
        return location and (
            location.usage != 'view') and location.company_id or False
