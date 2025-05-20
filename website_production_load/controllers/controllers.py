# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import base64
from odoo import _, fields, http
from odoo.http import request
from werkzeug.utils import redirect


class WebsiteProductionLoad(http.Controller):

    @http.route(['/start_production_load'], method="post", type='http', auth='user', website=True, csrf=False)
    def request(self, **post):
        """
        Browses all sale order, variants products, workcenters, quality tags
        in backend and returns them to the web page
        """
        user = request.env.user
        workcenter = request.env['mrp.workcenter'].sudo().search([
            ('website_published', '=', True),
            ('daily_load_available', '=', True),
            ('company_id', '=', user.company_id.id)])
        workcenter_dict = []
        for record in workcenter:
            workcenter_dict.append({'id': record.id, 'name': record.name})

        operation = request.env['mrp.operation'].sudo().search([
            ('daily_load_available_op', '=', True)])
        operation_dict = []
        for record in operation:
            operation_dict.append({'id': record.id, 'name': record.name})

        return http.request.render(
            'website_production_load.start_production_load', {
                'workcenter_selection': workcenter_dict,
                'operation_selection': operation_dict,
            })

    @http.route('/production_load-submit', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def send_request(self, **post):
        """
        Searches for related employee of the currently logged in user.
        The maintenance request is only created if the logged in user is an employee
        """
        employee = request.env['hr.employee'].sudo().search([
            ('consecutive_id', '=', post['employee'])])

        if not employee:
            return http.request.render(
                "website_production_load.error_production_load",
                {'msg_error': 'No se encontro el empleado'}
            )

        product_id = 0
        for key in post.keys():
            if 'product_' in key:
                product_id = int(key.split('_')[1])

        values = {
            'work_id': post['workcenter'],
            'product_id': product_id,
            'quantity': int(post['prod_load_qty']),
            'employee_id': employee.id,
            'operation_id': post['operation'],
            'daily_observations': post['comments'],
        }
        sudo_daily_load = request.env['mrp.production.daily.load'].sudo().create(values)

        request.env.ref('website_production_load.production_load_ticket').sudo()\
            .with_context(discard_logo_check=True).print_document(sudo_daily_load.id)

        return redirect('/start_production_load')
