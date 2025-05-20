# -*- coding: utf-8 -*-
# © 2018 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class OrderCheckExceptionsWizard(models.TransientModel):
    _name = 'order.check.exceptions.wizard'
    _description = 'descripcion pendiente'

    @api.multi
    def check_exceptions_wizard(self):
        sale_obj = self.env['sale.order']
        sale_var = sale_obj.search([('approve', '=', 'approved'), ('state', 'in', ('draft','sale','sent'))])
        for order in sale_var:
            if order.company_id.is_manufacturer:
                # order._product_data_validation()
                order.product_data_validation2()
