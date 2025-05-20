# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from io import StringIO
from datetime import datetime
from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.addons.report_tags.models import code128
import pytz

format_exception = {
    'report_tags.paperformat_tag': ['4', '7'],
    'report_tags.paperformat_tag_letter_vertical': ['6']
}
skip_code_customer = ['6']


class ParticularReport(models.AbstractModel):
    _name = 'report.report_tags.report_tag_customizable_order'
    _description = 'Report Tags customizable order'

    @api.model
    def code128_format(self, data):
        return code128.code128_format(data)

    @api.model
    def code128_image(self, data):
        image_new = code128.code128_image(data)
        buffer = StringIO.StringIO()
        image_new.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue())

    @api.model
    def jv_template5(self, commitment_date, date_reception):
        if not commitment_date or not date_reception:
            return ' '
        date_requested = commitment_date
        date_requested = pytz.timezone('UTC').localize(
            date_requested, is_dst=False)
        if self.env.context.get('tz'):
            date_requested = date_requested.astimezone(pytz.timezone(
                self.env.context.get('tz')))

        reception_date = date_reception

        year = reception_date.strftime("%Y")
        days = str((
            datetime.date(date_requested) - reception_date).days).zfill(3)
        return year + days

    def check_fields_template_5(self, order):
        if not order.commitment_date:
            raise ValidationError(
                "El pedido %s no tiene una fecha de solicitud" % (
                    order.name))
        if not order.date_reception:
            raise ValidationError(
                "El pedido %s no tiene una fecha de recepcion" % (
                    order.name))
        # if not order.bc_value:
        #     raise ValidationError(
        #         "El pedido %s no tiene un valor de codigo de barras" % (
        #             order.name))
        if not order.partner_id.vendor_code:
            raise ValidationError(
                "El cliente %s no tiene un codigo de vendedor" % (
                    order.partner_id.name))

    def change_paper_format(self, report, template):
        paperformat = 'report_tags.paperformat_tag_vertical'
        for paper, templates in format_exception.items():
            if template in templates:
                paperformat = paper
        report.sudo().write({'paperformat_id': self.env.ref(paperformat).id})

    @api.multi
    def _get_report_values(self, docids, data=None):
        report = self.env.ref('report_tags.tag_customizable_order')
        orders = self.env['sale.order'].browse(docids)
        code_customer = {}

        template = list(set(orders.mapped('partner_id').mapped('template_label')))
        if len(template) > 1:
            raise ValidationError("All customers must have the same template.")
        template = template[0]

        for order in orders:
            if template == '5':
                self.check_fields_template_5(order)

            if template not in skip_code_customer:
                for line in order.order_line:
                    code_customer[line.id] = self.env[
                        'product.product.customer'].search(
                            [('product_id', '=', line.product_id.id),
                             ('partner_id', '=', order.partner_id.id)],
                            limit=1)
                    if not code_customer[line.id]:
                        raise ValidationError(
                            "The product %s does not have code for this client" % (
                                line.product_id.name))
                    if template == '5' and not code_customer[line.id].bc_value:
                        raise ValidationError(
                            "The product %s does not have bc value for this client" % (
                                line.product_id.name))
                    if order.partner_id.type_barcode == 'UPC_A':
                        try:
                            if template != '7':
                                int(code_customer[line.id].customer_code)
                            else:
                                int(code_customer[line.id].bc_value)
                        except Exception:
                            raise ValidationError(
                                "The UPC-A barcode only accepts number format, please check the customer code of %s" % (
                                    line.product_id.default_code))

        self.change_paper_format(report, template[0])

        langs = self.env['res.lang'].search(
            [('active', '=', True)]).mapped('code')

        docargs = {
            'data': data,
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': orders,
            'code_customer': code_customer,
            'langs': langs,
            'code128_format': self.code128_format,
            'code128_image': self.code128_image,
            'jv_template5': self.jv_template5,
        }

        return docargs
