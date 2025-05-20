# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape
from odoo.addons.account_reports.controllers.main import FinancialReportController  # noqa


class FinancialReportControllerInhe(FinancialReportController):

    @http.route('/account_reports/<string:output_format>/<string:report_name>/<string:report_id>', type='http', auth='user')  # noqa
    def report(self, output_format, report_name, token, report_id=None, **kw):
        result = super(FinancialReportControllerInhe, self).report(
            output_format, report_name, token, report_id=report_id, **kw)
        uid = request.session.uid
        domain = [('create_uid', '=', uid)]
        report_model = request.env['account.report.context.common'].\
            get_full_report_name_by_report_name(report_name)
        report_obj = request.env[report_model].sudo(uid)
        if report_name == 'financial_report':
            report_id = int(report_id)
            domain.append(('report_id', '=', report_id))
            report_obj = report_obj.browse(report_id)
        context_obj = request.env[
            'account.report.context.common'].get_context_by_report_name(
                report_name)
        context_id = context_obj.sudo(uid).search(domain, limit=1)
        try:
            if output_format == 'txt':
                content = context_id.get_xml()
                response = request.make_response(
                    content,
                    headers=[
                        ('Content-Type', 'application/vnd.sun.xml.writer'),
                        ('Content-Disposition', 'attachment; filename=' + report_obj.get_name() + '.txt;'),  # noqa
                        ('Content-Length', len(content))
                    ]
                )
                response.set_cookie('fileToken', token)
                return response
            return result
        except BaseException as e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))
        else:
            return request.not_found()
