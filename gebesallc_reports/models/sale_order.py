# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
import base64

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    spiff_number = fields.Char(
        string='SPIFF number',
    )
    spiff_percent = fields.Float(
        string='% SPIFF',
    )

    def print_shipment_label_crossover(self):
        self.ensure_one()
        order_cross = self.env['sale.order'].sudo().search([
            ('supplier_ref', '=', self.name),
            ('state', '=', 'done'),
            ('company_id', '!=', self.company_id.id)])
        if not order_cross:
            raise UserError(_('This Sale order does not come from multicompany'))

        namepdf = ('%s-Shipment_label.pdf' % (
            order_cross.name))

        report = self.env['ir.actions.report'].sudo()._get_report_from_name(
            'report_tags.report_so_shipment_tag_debranded')

        pdf = report.sudo().render_qweb_pdf(order_cross.id)[0]

        data_attach = {
            'name': namepdf,
            'datas': base64.b64encode(pdf or b''),
            'datas_fname': namepdf,
            'res_model': 'sale.order',
            'res_id': self.id,
        }
        attachment_id = self.env['ir.attachment'].sudo().create(data_attach)

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=ir.attachment&id={id}&field=datas'
                   '&filename_field=datas_fname&download=true&filename={name}'
                   .format(id=attachment_id.id, name=attachment_id.name),
            'target': 'new',
        }

    def apply_spiff(self):
        ir_config = self.env['ir.config_parameter'].sudo()
        for sale in self:
            if not sale.spiff_number:
                if sale.user_id:
                    ref = sale.user_id.partner_id.ref
                    perc = float(ir_config.get_param(
                        'spiff.sale.percent', default='0.0'))

                    sale.write({
                        'spiff_number': ref,
                        'spiff_percent': perc
                    })
            else:
                sale.write({
                    'spiff_number': '',
                    'spiff_percent': 0.0
                })
