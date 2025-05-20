# -*- coding: utf-8 -*-
# Copyright 2017, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.website_quote.controllers.main import sale_quote
from odoo.addons.web import http
from odoo.addons.web.http import request
from odoo.tools.translate import _


class SaleQuote(sale_quote):

    # @http.route(['/quote/accept'], type='json', auth="public", website=True)
    # def accept(self, order_id, token=None, signer=None, sign=None, **post):
    #     # import pdb
    #     # pdb.set_trace()
    #     return request.website.render(
    #         'website.http_error', {
    #             'status_code': 'Forbidden',
    #             'status_message': _(
    #                 'You cannot add options to a confirmed order.')})

    # @http.route(['/quote/<int:order_id>/<token>/decline'], type='http', auth="public", methods=['POST'], website=True)
    # def decline(self, order_id, token, **post):
    #     # import pdb
    #     # pdb.set_trace()
    #     return request.website.render(
    #         'website.http_error', {
    #             'status_code': 'Forbidden',
    #             'status_message': _(
    #                 'You cannot add options to a confirmed order.')})
