# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class PurchaseOrderStateHist(models.Model):

    _name = 'purchase.order.state.hist'
    _description = 'descripcion pendiente'

    purchase_id = fields.Many2one('purchase.order',
                                  string='Solicitud de presupuesto')
    date = fields.Date(string='Date')
    status_old = fields.Char(string='Last Status')
    status_new = fields.Char(string='New Status')
