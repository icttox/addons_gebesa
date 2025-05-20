# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import base64
from odoo import _, fields, http
from odoo.http import request
from werkzeug.utils import redirect


class AlertQuality(http.Controller):

    @http.route(['/alert_quality'], method="post", type='http', auth='user', website=True, csrf=False)
    def request(self, **post):
        """
        Browses all sale order, variants products, workcenters, quality tags
        in backend and returns them to the web page
        """
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search(
            [('user_id', '=', user.id)])

        if not employee:
            return redirect('/alert_quality-nouser')

        # sale_order = request.env['sale.order'].sudo().search(
        #     [('state', 'in', ['done', 'closed']),
        #      ('company_id', '=', user.company_id.id),
        #      ('geb_invoice_status', '!=', 'total_invoice')], limit=300,)
        # product = request.env['product.product'].sudo().search([], limit=100)
        workcenter = request.env['mrp.workcenter'].sudo().search([
            ('website_published', '=', True)])
        flaw = []
        if workcenter:
            flaw = request.env['quality.alert.flaw'].sudo().search([
                ('workcenter_ids', 'in', workcenter[0].id)])

        # sale_order_dict = []
        # for record in sale_order:
        #     sale_order_dict.append({'id': record.id, 'name': record.name})
        # sale_order_dict = sorted(
        #     sale_order_dict, key=lambda sod: sod['name'], reverse=True)

        product_dict = []
        production = request.env['mrp.production'].sudo().search(
            [('sale_id', '=', False),
             ('create_date', '>', '2020-08-01')])
        product = production.mapped('product_id').mapped('id')
        product = request.env['product.product'].sudo().search(
            [('id', 'in', product)])

        for record in product.with_context(lang='es_MX'):
            name = '[' + record.default_code + '] '
            if record.individual_name:
                name += record.individual_name
            else:
                name += record.product_tmpl_id.name
            product_dict.append({'id': record.id, 'name': name})

        workcenter_dict = []
        for record in workcenter:
            workcenter_dict.append({'id': record.id, 'name': record.name})

        flaw_dict = []
        for record in flaw:
            flaw_dict.append({'id': record.id, 'name': record.display_name})

        return http.request.render('website_quality.Quality', {
            # 'so_selection': sale_order_dict,
            'product_selection': product_dict,
            'workcenter_selection': workcenter_dict,
            'flaw_selection': flaw_dict,
            'default_date': fields.Date.today(),
        })

    @http.route('/alert_quality-submit', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def send_request(self, **post):
        """
        Searches for related employee of the currently logged in user.
        The maintenance request is only created if the logged in user is an employee
        """
        user = request.env.user.id
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user)])
        error = ""

        if not employee:
            return redirect('/alert_quality-nouser')

        sale_id = False
        if post['order']:
            sale_id = request.env['sale.order'].sudo().search([
                ('name', '=', post['order'])])
            if not sale_id:
                error += _("Order %s not found,\n") % (post['order'])

        product = request.env['product.product'].sudo().search([
            ('id', '=', post['product'])])
        if not product:
            error += _("Product %s not found") % (post['product'])

        flaw_id = request.env['quality.alert.flaw'].sudo().search([
            ('id', '=', post['flaw'])])
        if int(post['workcenter']) not in flaw_id.workcenter_ids.ids:
            error += _(
                "defect %s does not correspond to the selected work center") % (
                flaw_id.code + '.-' + flaw_id.name)

        if error != "":
            return redirect('/alert_quality/error?error=%s' % (error))

        data = post.get('warning_evidence').read()
        values = {
            'title': post['subject'],
            'date': post['date'],
            'oven': post['oven'],
            'color': post['color'],
            'product_id': product.id,
            'product_tmpl_id': product.product_tmpl_id.id,
            'workcenter_id': post['workcenter'],
            'qty_reviewed': post['rev_qty'],
            'qty_rejected': post['rej_qty'],
            'flaw_id': post['flaw'],
            'provision': post['provision'],
            'description': post['descripcion'],
            'image': base64.b64encode(data)
        }
        if sale_id:
            values['sale_id'] = sale_id.id
        alert_id = request.env['quality.alert'].sudo().create(values)
        template = request.env.ref('website_quality.mail_template_alert_quality')
        template.sudo().send_mail(alert_id.id, force_send=True)

        return redirect('/alert_quality-thanks')

    @http.route(['/alert_quality/error'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def luch_thanks(self, **kw):

        error = kw.get('error')
        # import ipdb; ipdb.set_trace()

        return http.request.render(
            "website_quality.quality_error",
            {'msg_error': error})
