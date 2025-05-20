# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, http
from odoo.http import request
from werkzeug.utils import redirect
import datetime
import pytz


class WebsiteWorkOrder(http.Controller):

    @http.route(['/start_workorders'], method="post", type='http',
                auth='user', website=True, csrf=False)
    def request(self, **post):
        """
        Browses all sale order, variants products, workcenters, quality tags
        in backend and returns them to the web page
        """
        user = request.env.user
        department = user.employee_ids.department_id
        workcenter = request.env['mrp.workcenter'].sudo().search([
            ('website_published', '=', True),
            ('hr_department_ids', 'in', [department.id]),
            ('company_id', '=', user.company_id.id)])
        workcenter_dict = []
        for record in workcenter:
            workcenter_dict.append({'id': record.id, 'name': record.name})

        return http.request.render(
            'website_workorders.start_workorders_form', {
                'workcenter_selection': workcenter_dict,
            })

    @http.route('/start_workorders-submit', type='http', auth='public',
                methods=['POST'], website=True, csrf=False)
    def send_request(self, **post):
        """
        Searches for related employee of the currently logged in user.
        The maintenance request is only created if the logged in user
        is an employee
        """

        workorders = request.env['mrp.workorder'].sudo().search([
            ('workcenter_id', '=', int(post['workcenter'])),
            ('product_id', '=', int(post['product'])),
            ('state', 'not in', ['done', 'cancel'])])
        workorder_dic = {}
        # import ipdb; ipdb.set_trace()
        for work in workorders:
            if not work.production_id.segment_line_ids:
                continue
            segment = work.production_id.segment_line_ids.segment_id
            if segment.state in ('draft', 'cancel', 'construction'):
                continue
            product = work.production_id.product_id
            operation = work.operation_id
            key = str(product.default_code) + '|' + str(
                operation.sequence) + '|' + str(segment.id)
            if key not in workorder_dic:
                workorder_dic[key] = {
                    'segment': segment.folio,
                    'product': product.default_code,
                    'operation': operation.name,
                    'workorder': '',
                    'qty': 0.00
                }
            workorder_dic[key]['workorder'] += str(work.id) + '|'
            workorder_dic[key]['qty'] += work.qty_remaining

        return http.request.render(
            'website_workorders.start_workorders_detail_form', {
                'workorder_dic': workorder_dic,
            })

    @http.route('/start_workorders_detail-submit', type='http', auth='public',
                methods=['POST'], website=True, csrf=False)
    def send_request_detail(self, **post):
        for workorders in post:
            # import ipdb; ipdb.set_trace()
            if 'date_' in workorders or 'comments_' in workorders:
                continue
            if post[workorders] == '':
                continue
            qty = int(post[workorders])
            workorders_ids = workorders.split('|')
            workorders_ids.pop()

            for workorder_id in workorders_ids:

                if qty == 0:
                    continue
                workorder = request.env['mrp.workorder'].sudo().search([
                    ('id', '=', int(workorder_id))])
                if workorder.qty_remaining > qty:
                    workorder.write({
                        'qty_produced': qty + workorder.qty_produced,
                        'state': 'progress'})
                    qty -= qty
                else:
                    qty_remaining = workorder.qty_remaining
                    workorder.write({
                        'qty_produced': qty_remaining + workorder.qty_produced,
                        'state': 'done',
                        'date_finished': fields.Datetime.now()})
                    qty -= qty_remaining

            values = {
                'work_id': workorder.workcenter_id.id,
                'product_id': workorder.product_id.id,
                'quantity': int(post[workorders]),
                'employee_id': request.env.user.employee_ids.id,
                'operation_id': workorder.operation_id.operation_id.id,
                'routing_line_id': workorder.operation_id.id,
                'segment_id': workorder.production_id.segment_line_ids.segment_id.id,
                'date_start': datetime.datetime.strptime(
                    post['date_s_' + workorders] + ' -0600',
                    '%m/%d/%Y %I:%M %p %z').astimezone(pytz.timezone('UTC')),
                'date': datetime.datetime.strptime(
                    post['date_e_' + workorders] + ' -0600',
                    '%m/%d/%Y %I:%M %p %z').astimezone(pytz.timezone('UTC')),
                'daily_observations': post['comments_' + workorders],
            }
            daily_load = request.env['mrp.production.daily.load'].sudo().create(values)

            # request.env.ref('website_production_load.production_load_ticket').sudo()\
            #     .with_context(discard_logo_check=True).print_document(sudo_daily_load.id)

        return redirect('/start_workorders')
