# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    usuariogps = fields.Char(
        string='Usuario',
        related='company_id.usuariogps',
        readonly=False,
    )
    passwordgps = fields.Char(
        string='Password',
        related='company_id.passwordgps',
        readonly=False,
    )
    urlecho = fields.Char(
        string='URL echo',
        related='company_id.urlecho',
        readonly=False,
    )

    tms_product_id = fields.Many2one(
        'product.product',
        related='company_id.tms_product_id',
        readonly=False,
        string='Product',
    )

    tms_location_id = fields.Many2one(
        'stock.location',
        related='company_id.tms_location_id',
        readonly=False,
        string='Origin Location',
    )

    tms_location_dest_id = fields.Many2one(
        'stock.location',
        related='company_id.tms_location_dest_id',
        readonly=False,
        string='Destination Location',
    )

    tms_type_adjustment_id = fields.Many2one(
        'type.adjustment',
        related='company_id.tms_type_adjustment_id',
        readonly=False,
        string='Type Adjustment',
    )

    tms_type_adjustment_ret_id = fields.Many2one(
        'type.adjustment',
        related='company_id.tms_type_adjustment_ret_id',
        readonly=False,
        string='Type of adjustment (return)',
    )

    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #     get_param = self.env['ir.config_parameter'].sudo().get_param
    #     tms_product_id = literal_eval(get_param(
    #         'tms.tms_product_id', default='False'))
    #     tms_location_id = literal_eval(get_param(
    #         'tms.tms_location_id', default='False'))
    #     tms_location_dest_id = literal_eval(get_param(
    #         'tms.tms_location_dest_id', default='False'))
    #     tms_type_adjustment_id = literal_eval(get_param(
    #         'tms.tms_type_adjustment_id', default='False'))
    #     tms_type_adjustment_ret_id = literal_eval(get_param(
    #         'tms.tms_type_adjustment_ret_id', default='False'))

    #     res.update(
    #         tms_product_id=tms_product_id,
    #         tms_location_id=tms_location_id,
    #         tms_location_dest_id=tms_location_dest_id,
    #         tms_type_adjustment_id=tms_type_adjustment_id,
    #         tms_type_adjustment_ret_id=tms_type_adjustment_ret_id,

    #     )
    #     return res

    # @api.multi
    # def set_values(self):
    #     super(ResConfigSettings, self).set_values()
    #     ICPSudo = self.env['ir.config_parameter'].sudo()
    #     ICPSudo.set_param(
    #         "tms.tms_product_id",
    #         self.tms_product_id.id)
    #     ICPSudo.set_param(
    #         "tms.tms_location_id",
    #         self.tms_location_id.id)
    #     ICPSudo.set_param(
    #         "tms.tms_location_dest_id",
    #         self.tms_location_dest_id.id)
    #     ICPSudo.set_param(
    #         "tms.tms_type_adjustment_id",
    #         self.tms_type_adjustment_id.id)
    #     ICPSudo.set_param(
    #         "tms.tms_type_adjustment_ret_id",
    #         self.tms_type_adjustment_ret_id.id)
