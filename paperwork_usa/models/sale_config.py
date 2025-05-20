# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    planned_delivery_date = fields.Text(
        related='company_id.planned_delivery_date',
        string='Planned Delivery Date',
        readonly=False)

    foreign_line_ids = fields.Many2many(
        related='company_id.foreign_line_ids',
        relation='product.line',
        readonly=False)

    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #     get_param = self.env['ir.config_parameter'].sudo().get_param
    #     planned_delivery_date = get_param(
    #         'paperwork_usa.planned_delivery_date', default='False')
    #     res.update(
    #         planned_delivery_date=planned_delivery_date,
    #     )
    #     return res

    # @api.multi
    # def set_values(self):
    #     super(ResConfigSettings, self).set_values()
    #     ICPSudo = self.env['ir.config_parameter'].sudo()
    #     ICPSudo.set_param(
    #         "paperwork_usa.planned_delivery_date",
    #         self.planned_delivery_date)

class ResCompany(models.Model):
    _inherit = 'res.company'

    planned_delivery_date = fields.Text(
        string='Planned Delivery Date')

    foreign_line_ids = fields.Many2many(
        'product.line',
        string='Líneas de productos no nacionales')
