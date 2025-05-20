# Copyright 2024, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models
from odoo.exceptions import ValidationError


class ParticularReport(models.AbstractModel):
    _name = 'report.report_tags.report_customer_code_grainger_tag'
    _description = 'Report Tags customer code Grainger'

    @api.multi
    def _get_report_values(self, docids, data=None):
        order_ids = self.env['sale.order'].browse(docids)
        cust_code = {}
        bom_lines = {}
        for order in order_ids:
            cust_code[order.id] = {}
            bom_lines[order.id] = {}
            for line in order.order_line:
                cusmtomer_code = self.env['product.product.customer'].search(
                    [('product_id', '=', line.product_id.id),
                     ('partner_id', '=', order.partner_id.id)])
                if not cusmtomer_code:
                    raise ValidationError(
                        "Al producto %s le falta el codigo para el cliente %s"
                        % (line.product_id.default_code, order.partner_id.name))

                cust_code[order.id][line.product_id.id] = cusmtomer_code

                bom = self.env['mrp.bom'].search(
                    [('product_id', '=', line.product_id.id),
                     ('active', '=', True),
                     ('type', '=', 'phantom')], limit=1)
                if bom:
                    bom_lines[order.id][line.product_id.id] = bom.bom_line_ids.filtered(lambda l: l.product_id)
                else:
                    bom_lines[order.id][line.product_id.id] = []

        docargs = {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': order_ids,
            'cust_code': cust_code,
            'bom_lines': bom_lines,
        }

        return docargs
