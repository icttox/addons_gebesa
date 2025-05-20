# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class RestApi(http.Controller):
    """This is a controller which is used to generate responses based on the
    api requests"""

    def get_default_session(self):
        return {
            'context': {},
            # 'lang': request.default_lang()  # must be set at runtime
            'db': None,
            'debug': '',
            'login': None,
            'uid': None,
            'session_token': None,
        }

    def get_json_error(self, error, code):
        request.endpoint.routing['save_session'] = False
        datas = json.dumps({
            "status": "Error",
            "error": error,
            "error_code": code
        })
        return datas

    def auth_api_key(self, api_key):
        """This function is used to authenticate the api-key when sending a
        request"""

        user_id = request.env['res.users'].search([('api_key', '=', api_key)])
        if api_key is not None and user_id:
            response = 'OK'
        elif not user_id:
            response = self.get_json_error('Invalid API Key!', '104')
        else:
            response = self.get_json_error('No API Key Provided!', '105')

        return response

    def generate_response(self, method, model, rec_id):
        """This function is used to generate the response based on the type
        of request and the parameters given"""
        option = request.env['connection.api'].search(
            [('model_id', '=', model)], limit=1)
        model_name = option.model_id.model

        if method != 'DELETE':
            data = json.loads(request.httprequest.data.decode())
        else:
            data = {}
        fields = []
        if data:
            for field in data['fields']:
                fields.append(field)
        if not fields and method != 'DELETE':
            return self.get_json_error('No fields selected for the model', '106')
        if not option:
            return self.get_json_error('No Record Created for the model', '107')
        try:
            if method == 'GET':
                fields = []
                for field in data['fields']:
                    fields.append(field)
                if not option.is_get:
                    return self.get_json_error('Get Method Not Allowed', '110')
                else:
                    datas = []
                    if rec_id != 0:
                        partner_records = request.env[
                            str(model_name)].search_read(
                            domain=[('id', '=', rec_id)],
                            fields=fields
                        )
                        data = json.dumps({
                            'records': partner_records
                        })
                        datas.append(data)
                        # return request.make_response(data=datas)
                        return datas
                    else:
                        partner_records = request.env[
                            str(model_name)].search_read(
                            domain=[],
                            fields=fields
                        )
                        data = json.dumps({
                            'records': partner_records
                        })
                        datas.append(data)
                        # return request.make_response(data=datas)
                        return datas
        except Exception as err:
            return self.get_json_error('Invalid JSON Data: \n %s' % str(err), '111')
        if method == 'POST':
            if not option.is_post:
                return self.get_json_error('POST Method Not Allowed', '120')
            else:
                try:
                    data = json.loads(request.httprequest.data.decode())
                    datas = []
                    new_resource = request.env[str(model_name)].create(
                        data['values'])
                    partner_records = request.env[
                        str(model_name)].search_read(
                        domain=[('id', '=', new_resource.id)],
                        fields=fields
                    )
                    new_data = json.dumps({'New resource': partner_records, })
                    datas.append(new_data)
                    # return request.make_response(data=datas)
                    return datas
                except Exception as err:
                    return self.get_json_error(
                        'Invalid JSON Data:\n %s' % str(err), '121')
        if method == 'PUT':
            if not option.is_put:
                return self.get_json_error('PUT Method Not Allowed', '130')
            else:
                if rec_id == 0:
                    return self.get_json_error('No ID Provided', '131')
                else:
                    resource = request.env[str(model_name)].browse(
                        int(rec_id))
                    if not resource.exists():
                        return self.get_json_error('Resource not found', '132')
                    else:
                        try:
                            datas = []
                            data = json.loads(
                                request.httprequest.data.decode())
                            resource.write(data['values'])
                            partner_records = request.env[
                                str(model_name)].search_read(
                                domain=[('id', '=', resource.id)],
                                fields=fields
                            )
                            new_data = json.dumps(
                                {'Updated resource': partner_records,
                                 })
                            datas.append(new_data)
                            # return request.make_response(data=datas)
                            return datas

                        except Exception as err:
                            return self.get_json_error(
                                'Invalid JSON Data:\n %s' % str(err), '133')
        if method == 'DELETE':
            if not option.is_delete:
                return self.get_json_error('Method Not Allowed', '140')
            else:
                if rec_id == 0:
                    return self.get_json_error('No ID Provided', '141')
                else:
                    resource = request.env[str(model_name)].browse(
                        int(rec_id))
                    if not resource.exists():
                        return self.get_json_error('Resource not found', '142')
                    else:
                        try:
                            records = request.env[
                                str(model_name)].search_read(
                                domain=[('id', '=', resource.id)],
                                fields=['id', 'display_name']
                            )
                            remove = json.dumps(
                                {"Resource deleted": records,
                                 })
                            resource.unlink()
                            # return request.make_response(data=remove)
                            return remove
                        except Exception as err:
                            return self.get_json_error(
                                'Invalid JSON Data:\n %s' % str(err), '143')

    @http.route(['/send_request'], type="json",
                auth='none',
                methods=['GET', 'POST', 'PUT', 'DELETE'], csrf=False)
    def fetch_data(self, **kw):
        """This controller will be called when sending a request to the
        specified url, and it will authenticate the api-key and then will
        generate the result"""
        username = request.httprequest.headers.get('login')
        password = request.httprequest.headers.get('password')
        api_key = request.httprequest.headers.get('api-key')

        try:
            request.session.authenticate(
                request.session.db,
                username,
                password
            )
        except Exception as err:
            return self.get_json_error(
                'Wrong login credentials:\n %s' % str(err), '102')
        auth_api = self.auth_api_key(api_key)
        if auth_api != 'OK':
            return auth_api

        model = request.httprequest.args['model']
        model_id = request.env['ir.model'].search(
            [('model', '=', model)])

        if not model_id:
            return self.get_json_error(
                '''Invalid model, check spelling or maybe the related
                module is not installed''', '103')

        if 'Id' not in request.httprequest.args:
            rec_id = 0
        else:
            rec_id = request.httprequest.args['Id']
        http_method = request.httprequest.method
        result = self.generate_response(http_method, model_id.id, rec_id)
        return result

    @http.route(['/odoo_connect'], type="http", auth="none", csrf=False,
                methods=['GET'])
    def odoo_connect(self, **kw):
        """This is the controller which initializes the api transaction by
        generating the api-key for specific user and database"""

        username = request.httprequest.headers.get('login')
        password = request.httprequest.headers.get('password')
        db = request.httprequest.headers.get('db')
        try:
            request.session.update(self.get_default_session(), db=db)
            auth = request.session.authenticate(request.session.db, username,
                                                password)
            user = request.env['res.users'].browse(auth)
            api_key = request.env.user.generate_api(username)
            datas = json.dumps({"Status": "auth successful",
                                "User": user.name,
                                "api-key": api_key})
            return request.make_response(data=datas)
        except Exception as err:
            return self.get_json_error(
                'Wrong login credentials:\n %s' % err,
                '101'
            )
