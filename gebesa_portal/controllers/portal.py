# Copyright 2021, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortalGebesa(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        values['shipment_count'] = request.env['sale.order'].search_count([
            ('state', 'in', ['sale', 'done']),
            ('geb_invoice_status', 'in', ['no_invoice', 'partial_invoice'])
        ])
        return values

    @http.route(['/my/ship_backorder', '/my/ship_backorder/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_shpment_backorder(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        domain = [
            ('message_partner_ids', 'child_of', [partner.parent_id.id]),
            ('state', 'in', ['sale', 'done']),
            ('geb_invoice_status', 'in', ['no_invoice', 'partial_invoice'])
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': ' so.date_order desc'},
            'departure': {'label': _('Departure Date'), 'order': ' ms.departure_date desc'},
            'code': {'label': _('Product Code'), 'order': ' pp.default_code'},
        }
        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain)

        # search the backorders to display, according to the pager data
        current_partner = partner.parent_id.id or partner.id
        params = [partner.company_id.id, current_partner]
        orders = request.env['sale.order'].get_backorder_data(params, sort_order)
        for order in orders:
            order['portal_url'] = request.env['sale.order'].sudo().browse(order['so_id']).get_portal_url()

        values.update({
            'date': date_begin,
            'orders': orders,
            'page_name': 'ship_backorder',
            'archive_groups': archive_groups,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'filterby': filterby,
            'default_url': '/my/ship_backorder',
        })
        return request.render("gebesa_portal.portal_my_shpment_backorder", values)
