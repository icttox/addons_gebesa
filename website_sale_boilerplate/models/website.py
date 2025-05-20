# -*- coding: utf-8 -*-
# Copyright 2019, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class Website(models.Model):
    _inherit = 'website'

    @api.multi
    def _prepare_sale_order_values(self, partner, pricelist):
        res = super()._prepare_sale_order_values(
            partner, pricelist)

        if partner.parent_id:
            res['partner_invoice_id'] = partner.parent_id.id

        return res
