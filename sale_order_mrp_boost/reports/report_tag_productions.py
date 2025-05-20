# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import ValidationError

class ReportTag(models.AbstractModel):
    _inherit = 'report.report_tags.report_tag1'

    def get_line_qty(self, productions):
        line_qty = {}
        for doc in productions:
            if doc not in line_qty:
                line_qty[doc.id] = {}
            if doc.sale_line_id:
                line_qty[doc.id][doc.sale_line_id] = doc.product_qty
            elif doc.sale_line_qty_info:
                for lines in doc.sale_line_qty_info.split('|'):
                    data = lines.split(':')
                    line_id = self.env['sale.order.line'].search([('id', '=', int(data[0]))])
                    if line_id not in line_qty[doc.id]:
                        line_qty[doc.id][line_id] = float(data[1])
                    else:
                        line_qty[doc.id][line_id] = line_qty[doc.id][line_id] + float(data[1])
            else:
                line_qty[doc.id][self.env['sale.order.line']] = doc.product_qty
        return line_qty


class ReportTagDebrand(models.AbstractModel):
    _inherit = 'report.report_tags.report_tag_debrand'

    def get_line_qty(self, productions):
        line_qty = {}
        for doc in productions:
            if doc not in line_qty:
                line_qty[doc.id] = {}
            if doc.sale_line_id:
                line_qty[doc.id][doc.sale_line_id] = doc.product_qty
            elif doc.sale_line_qty_info:
                for lines in doc.sale_line_qty_info.split('|'):
                    data = lines.split(':')
                    line_id = self.env['sale.order.line'].search([('id', '=', int(data[0]))])
                    if line_id not in line_qty[doc.id]:
                        line_qty[doc.id][line_id] = float(data[1])
                    else:
                        line_qty[doc.id][line_id] = line_qty[doc.id][line_id] + float(data[1])
            else:
                line_qty[doc.id][self.env['sale.order.line']] = doc.product_qty
        return line_qty


class ReportTagProd24(models.AbstractModel):
    _inherit = 'report.report_tags.report_tag_prod_2_4'

    def get_customer_code(self, productions):
        code_customer = {}

        for prod in productions:
            customer_code = False
            if prod.partner_id:
                partner_id = prod.partner_id
            else:
                partner_id = prod.sale_order_line_ids[0].order_partner_id
            customer_code = self.env['product.product.customer'].search([
                ('product_id', '=', prod.product_id.id),
                ('partner_id', '=', partner_id.id)])
            if not customer_code:
                raise ValidationError("The product %s does not have code for this client %s" % (prod.product_id.name, partner_id.name))
            code_customer[prod.id] = {
                'customer_code': customer_code,
                'partner_id': partner_id
            }
        return code_customer


class ReportTagProd24SinBarcode(models.AbstractModel):
    _inherit = 'report.report_tags.report_tag_prod_2_4_sin_barcode'

    def get_customer_code(self, productions):
        code_customer = {}

        for prod in productions:
            customer_code = False
            if prod.partner_id:
                partner_id = prod.partner_id
            else:
                partner_id = prod.sale_order_line_ids[0].order_partner_id
            customer_code = self.env['product.product.customer'].search([
                ('product_id', '=', prod.product_id.id),
                ('partner_id', '=', partner_id.id)])
            if not customer_code:
                raise ValidationError("The product %s does not have code for this client %s" % (prod.product_id.name, partner_id.name))
            code_customer[prod.id] = {
                'customer_code': customer_code,
                'partner_id': partner_id
            }
        return code_customer


class ReportTagCustomizable(models.AbstractModel):
    _inherit = 'report.report_tags.report_tag_customizable'

    def get_template(self, production):
        template = set(production.mapped('partner_id').mapped('template_label'))
        template2 = set(production.mapped('partner_ids').mapped('template_label'))

        template = list(template | template2)
        if len(template) > 1:
            raise ValidationError("All customers must have the same template.")
        return template[0]

    def get_customer_code(self, production):
        if production.partner_id:
            partner_id = production.partner_id
        else:
            partner_id = production.sale_order_line_ids[0].order_partner_id

        customer_code = self.env['product.product.customer'].search([
            ('product_id', '=', production.product_id.id),
            ('partner_id', '=', partner_id.id)], limit=1)

        if not customer_code:
            raise ValidationError(
                "The product %s does not have code for this client" % (
                    production.product_id.name))

        return {
            'customer_code': customer_code,
            'partner_id': partner_id
        }

    def get_line_qty(self, productions):
        line_qty = {}
        for doc in productions:
            if doc not in line_qty:
                line_qty[doc.id] = {}
            if doc.sale_line_id:
                line_qty[doc.id][doc.sale_line_id] = doc.product_qty
            elif doc.sale_line_qty_info:
                for lines in doc.sale_line_qty_info.split('|'):
                    data = lines.split(':')
                    line_id = self.env['sale.order.line'].search([('id', '=', int(data[0]))])
                    if line_id not in line_qty[doc.id]: 
                        line_qty[doc.id][line_id] = float(data[1])
                    else:
                        line_qty[doc.id][line_id] = line_qty[doc.id][line_id] + float(data[1])
            else:
                line_qty[doc.id][self.env['sale.order.line']] = doc.product_qty
        return line_qty

    def check_fields_template_5(self, prod):
        if prod.sale_id:
            super().check_fields_template_5(prod)
            return
        for sale in prod.sale_order_ids:
            if not sale.commitment_date:
                raise ValidationError(
                    "El pedido %s no tiene una fecha de solicitud" % (
                        sale.name))
            if not sale.date_reception:
                raise ValidationError(
                    "El pedido %s no tiene una fecha de recepcion" % (
                        sale.name))
            if not sale.partner_id.vendor_code:
                raise ValidationError(
                    "El cliente %s no tiene un codigo de vendedor" % (
                        sale.partner_id.name))
