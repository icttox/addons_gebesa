# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author:SAURABH P V(<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import base64
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal
from werkzeug.utils import redirect


class MaintenanceRequest(http.Controller):

    @http.route(['/maintenance_request'], method="post", type='http', auth='user', website=True, csrf=False)
    def request(self, **post):
        # import ipdb; ipdb.set_trace()
        """
        Browses all maintenance teams and equipments in backend and returns them to the web page
        """
        # Maquinas y Herramientas

        maintenance_team = request.env['maintenance.team'].sudo(
        ).search([('website_published', '=', True)])

        categorys = request.env['maintenance.equipment.category'].sudo(
        ).search([('website_published', '=', True)])

        ubication = request.env['res.physical.location'].sudo().search([
            ('website_published', '=', True)])

        maintenance_requests = []
        if categorys and ubication:
            maintenance_requests = request.env['maintenance.equipment'].sudo().search([
                ('maintenance_team_id', 'in', maintenance_team.ids),
                ('category_id', 'in', categorys.ids),
                ('location_physical', 'in', ubication.ids)])

        user = request.env.user.id
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user)])

        ubication_dict = []
        request_dict = []
        team_name = []

        for record in ubication:
            name = record.name
            ubication_dict.append({'id': record.id, 'name': name})
            pass
        for record in maintenance_requests:
            name = record.name
            request_dict.append({'id': record.id, 'name': name})
        for record in maintenance_team:
            name = record.name
            team_name.append({'id': record.id, 'name': name})

        if employee:
            return http.request.render('website_maintenance_hr.Maintenance', {
                'ubication_selection': ubication_dict,
                'equipment_selection': request_dict,
                'team_selection': team_name,
            })
        return redirect('/maintenance_request-nouser')

    @http.route('/submit', method='post', type='http', auth='public', website=True, csrf=False)
    def send_request(self, **post):
        """
        Searches for related employee of the currently logged in user.
        The maintenance request is only created if the logged in user is an employee
        """
        user = request.env.user.id
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user)])
        if employee:
            data = post.get('warning_evidence').read()
            values = {
                # 'name': post['subject'],
                'maintenance_team_id': post['teams'],
                'equipment_id': post['equipment'],
                'description': post['details'],
                'priority': post['stars'],
                'employee_id': employee.id,
                'image': base64.b64encode(data),
            }
            request_id = request.env['maintenance.request'].sudo().create(values)
            request_id.onchange_equipment_id()
            template = request.env.ref('website_maintenance_hr.mail_template_maintenance_request')
            template.sudo().send_mail(request_id.id, force_send=True)

            return redirect('/maintenance_request-thanks')

        return redirect('/maintenance_request-nouser')


class CustomerPortal(portal.CustomerPortal):

    @http.route(['/equipments/<int:equipment_id>'], type='http', auth='user', website=True)
    def equipment(self, equipment_id=None):
        equipment = request.env['maintenance.equipment'].sudo().search([('id', '=', equipment_id)])

        if not equipment:
            return request.render("website.404")

        attachments = request.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'maintenance.equipment'),
            ('res_id', '=', equipment.id)])

        return request.render("website_maintenance_hr.equipment_details", {
            'equipment': equipment,
            'attachments': attachments,
            'page_name': 'equipment',
        })
