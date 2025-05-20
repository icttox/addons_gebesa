# Copyright 2022, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, http
from odoo.http import request
from werkzeug.utils import redirect
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.tools import consteq


class HrLunch(http.Controller):

    def _get_lunch_order_data(self, identification_id, lunch_pass):
        data = {}

        employee = request.env['hr.employee'].sudo().search(
            [('identification_id', '=', identification_id)])
        if not employee:
            data['error'] = 'No se encontro el empleado con el numero: ' + identification_id
            return data
        data['employee'] = employee

        decryptpass = employee.decrypt_password_as_string(employee.id)
        if lunch_pass != decryptpass.upper():
            data['error'] = 'La contraseña no coincide con empleado con el numero: ' + identification_id
            return data

        product = request.env.ref('website_lunch_hr.producto_platillo')
        if not product:
            data['error'] = 'No se encontro un producto para la comida'
            return data
        data['product'] = product

        return data

    def _create_lunch_order(self, data):
        values_order = {
            'user_id': data['user'],
            'employee_id': data['employee'].id,
            'state': 'confirmed',
            'order_line_ids': [],
        }

        order_id = request.env['lunch.order'].sudo().create(values_order)

        values = {
            'product_id': data['product'].id,
            'state': 'confirmed',
            'note': 'Creado desde website',
            'order_id': order_id.id,
        }

        order_line_id = request.env['lunch.order.line'].sudo().create(values)

        return order_line_id

    def _document_check_access(self, model_name, document_id, access_token=None):
        document = request.env[model_name].browse([document_id])
        document_sudo = document.sudo().exists()
        if not document_sudo:
            raise MissingError(_("This document does not exist."))
        try:
            document.check_access_rights('read')
            document.check_access_rule('read')
        except AccessError:
            if not access_token or not consteq(document_sudo.access_token, access_token):
                raise
        return document_sudo

    # METAL #

    @http.route(['/gebesa_metal_lunch'], method="post", type='http', auth='user', website=True, csrf=False)
    def request_metal(self, **post):
        """
        Browses all sale order, variants products, workcenters, quality tags
        in backend and returns them to the web page
        """
        user = request.env.user
        return http.request.render('website_lunch_hr.HrLunchMetal', {})

    @http.route('/gebesa_metal_lunch-submit', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def send_request_metal(self, **post):
        """
        """
        user = request.env.user.id
        if not user:
            return redirect('/gebesa_metal_lunch/error?error=%s' % ('error'))

        try:
            post_data = post['identification_id']
            identification_id, lunch_pass = post_data.split('-')
            data = self._get_lunch_order_data(identification_id, lunch_pass)

            if 'error' in data:
                # return redirect('/alert_quality/error?error=%s' % (error))
                return redirect('/gebesa_metal_lunch/error?error=%s' % (data['error']))

            data['user'] = user
            order_line_id = self._create_lunch_order(data)
        except Exception as err:
            if ValidationError == type(err):
                err = err.name
            return redirect('/gebesa_metal_lunch/error?error=%s' % (err))

        return redirect('/gebesa_metal_lunch/order/%d?download=false' % order_line_id.id)

        # return redirect('/gebesa_metal_lunch/thanks?order_line_id=%d' % order_line_id.id)

    @http.route(['/gebesa_metal_lunch/thanks'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def luch_thanks_metal(self, **kw):

        order_line_id = int(kw.get('order_line_id', -1))

        if not order_line_id:
            return redirect('/gebesa_metal_lunch/error?error=%s' % ('No se encontro el pedido'))

        order_line = request.env['lunch.order.line'].sudo().search(
            [('id', '=', order_line_id)])

        if not order_line:
            return redirect('/gebesa_metal_lunch/error?error=%s' % ('No se encontro la linea del pedido'))

        return request.render("website_lunch_hr.HrLunchMetalThnx", {'order_line': order_line})

    @http.route(['/gebesa_metal_lunch/order/<int:order_id>'], type='http', auth="public", website=True)
    def portal_lunch_order_detail_metal(self, order_id, access_token=None, report_type=None, download=False, **kw):
        try:
            order_sudo = self._document_check_access('lunch.order.line', order_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/gebesa_metal_lunch')

        if not order_sudo.was_printed:
            request.env.ref('website_lunch_hr.action_lunch_metal_ticket').sudo()\
                .with_context(discard_logo_check=True).print_document(order_sudo.id)
            order_sudo.was_printed = True

        return request.redirect('/gebesa_metal_lunch')

    @http.route(['/gebesa_metal_lunch/error'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def luch_error_metal(self, **kw):

        error = kw.get('error')
        if error == '':
            error = 'No puede hacer pedidos de almuerzo ya que la información del empleado es incorrecta.'

        return http.request.render(
            "website_lunch_hr.gebesa_metal_lunch_error",
            {'msg_error': error})

    # MADERA #

    @http.route(['/gebesa_madera_lunch'], method="post", type='http', auth='user', website=True, csrf=False)
    def request_madera(self, **post):
        """
        Browses all sale order, variants products, workcenters, quality tags
        in backend and returns them to the web page
        """
        user = request.env.user
        return http.request.render('website_lunch_hr.HrLunchMadera', {})

    @http.route('/gebesa_madera_lunch-submit', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def send_request_madera(self, **post):
        """
        """
        user = request.env.user.id
        if not user:
            return redirect('/gebesa_madera_lunch/error?error=%s' % ('error'))

        try:
            post_data = post['identification_id']
            identification_id, lunch_pass = post_data.split('-')
            data = self._get_lunch_order_data(identification_id, lunch_pass)

            if 'error' in data:
                # return redirect('/gebesa_madera_lunch-noemployee')
                return redirect('/gebesa_madera_lunch/error?error=%s' % (data['error']))

            data['user'] = user
            order_line_id = self._create_lunch_order(data)
        except Exception as err:
            if ValidationError == type(err):
                err = err.name
            return redirect('/gebesa_madera_lunch/error?error=%s' % (err))

        return redirect('/gebesa_madera_lunch/order/%d?download=false' % order_line_id.id)

        # return redirect('/gebesa_madera_lunch/thanks?order_line_id=%d' % order_line_id.id)

    @http.route(['/gebesa_madera_lunch/thanks'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def luch_thanks_madera(self, **kw):

        order_line_id = int(kw.get('order_line_id', -1))

        if not order_line_id:
            return redirect('/gebesa_madera_lunch/error?error=%s' % ('No se encontro el pedido'))

        order_line = request.env['lunch.order.line'].sudo().search(
            [('id', '=', order_line_id)])

        if not order_line:
            return redirect('/gebesa_madera_lunch/error?error=%s' % ('No se encontro la linea del pedido'))

        return request.render("website_lunch_hr.HrLunchMaderaThnx", {'order_line': order_line})

    @http.route(['/gebesa_madera_lunch/order/<int:order_id>'], type='http', auth="public", website=True)
    def portal_lunch_order_detail_madera(self, order_id, access_token=None, report_type=None, download=False, **kw):
        try:
            order_sudo = self._document_check_access('lunch.order.line', order_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/gebesa_madera_lunch')

        if not order_sudo.was_printed:
            request.env.ref('website_lunch_hr.action_lunch_madera_ticket').sudo()\
                .with_context(discard_logo_check=True).print_document(order_sudo.id)
            order_sudo.was_printed = True

        return request.redirect('/gebesa_madera_lunch')

    @http.route(['/gebesa_madera_lunch/error'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def luch_error_madera(self, **kw):

        error = kw.get('error')
        if error == '':
            error = 'No puede hacer pedidos de almuerzo ya que la información del empleado es incorrecta.'

        return http.request.render(
            "website_lunch_hr.gebesa_madera_lunch_error",
            {'msg_error': error})
