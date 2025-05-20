# -*- coding: utf-8 -*-
# © 2021, Leslie Marquez
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
    _name = 'report.report_tags.report_tag_customizable'
    _description = 'Report Tags customizable'

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

    def check_fields_template_5(self, prod):
        if not prod.sale_id.commitment_date:
            raise ValidationError(
                "El pedido %s no tiene una fecha de solicitud" % (
                    prod.sale_id.name))
        if not prod.sale_id.date_reception:
            raise ValidationError(
                "El pedido %s no tiene una fecha de recepcion" % (
                    prod.sale_id.name))
        if not prod.partner_id.vendor_code:
            raise ValidationError(
                "El cliente %s no tiene un codigo de vendedor" % (
                    prod.sale_id.partner_id.name))

    def change_paper_format(self, report, template):
        paperformat = 'report_tags.paperformat_tag_vertical'
        for paper, templates in format_exception.items():
            if template in templates:
                paperformat = paper
        report.sudo().write({'paperformat_id': self.env.ref(paperformat).id})

    def get_template(self, production):
        template = list(set(production.mapped('partner_id').mapped('template_label')))
        if len(template) > 1:
            raise ValidationError("All customers must have the same template.")
        return template[0]

    def get_customer_code(self, production):
        customer_code = self.env['product.product.customer'].search([
            ('product_id', '=', production.product_id.id),
            ('partner_id', '=', production.partner_id.id)], limit=1)

        if not customer_code:
            raise ValidationError(
                "The product %s does not have code for this client" % (
                    prod.product_id.name))

        return {
            'customer_code': customer_code,
            'partner_id': production.partner_id
        }

    def get_line_qty(self, productions):
        line_qty = {}
        for doc in productions:
            if doc not in line_qty:
                line_qty[doc.id] = {doc.sale_line_id: doc.product_qty}
        return line_qty

    @api.multi
    def _get_report_values(self, docids, data=None):
        report = self.env.ref('report_tags.tag_customizable')
        production = self.env['mrp.production'].browse(docids)
        code_customer = {}

        template = self.get_template(production)

        for prod in production:
            if template == '5':
                self.check_fields_template_5(prod)

            if template not in skip_code_customer:
                code_customer[prod.id] = self.get_customer_code(prod)

                if template == '5' and not code_customer[prod.id]['customer_code'].bc_value:
                    raise ValidationError(
                        "The product %s does not have bc value for this client" % (
                            prod.product_id.name))
                if prod.partner_id.type_barcode == 'UPC_A':
                    try:
                        if template != '7':
                            int(code_customer[prod.id]['customer_code'].customer_code)
                        else:
                            int(code_customer[prod.id]['customer_code'].bc_value)
                    except Exception:
                        raise ValidationError(
                            "The UPC-A barcode only accepts number format, please check the customer code of %s" % (
                                prod.product_id.default_code))

        self.change_paper_format(report, template[0])

        langs = self.env['res.lang'].search(
            [('active', '=', True)]).mapped('code')

        line_qty = self.get_line_qty(production)

        docargs = {
            'data': data,
            'doc_ids': docids,
            'doc_model': 'mrp.production',
            'docs': production,
            'code_customer': code_customer,
            'langs': langs,
            'line_qty': line_qty,
            'code128_format': self.code128_format,
            'code128_image': self.code128_image,
            'jv_template5': self.jv_template5,
            'template': template,
        }

        return docargs
