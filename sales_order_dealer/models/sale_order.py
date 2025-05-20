# -*- coding: utf-8 -*-
# Copyright 2018, Esther Cisneros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo import SUPERUSER_ID
from dateutil.relativedelta import relativedelta


def update_table(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute('ALTER TABLE sale_order ALTER COLUMN partner_shipping_id DROP NOT NULL')


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    def _compute_delivery_date(self):

        # self.customer_delivery_date = fields.Date.context_today(self)
        self.customer_delivery_date = False

        shipments = self.env['mrp.shipment.line'].search([
            ('sale_order_id', '=', self.id),
            ('quantity_shipped', '>', 0)]).mapped('shipment_id').filtered(
            lambda shp: shp.state == 'finished').sorted(
            key=lambda ship: ship.departure_date, reverse=True)

        if not shipments:
            return

        # Not too acurate because the travel must include multiple
        # deliveries for different customers, date end real indicate
        # the finish of the whole travel
        travels = self.env['tms.travel'].sudo().search([
            ('shipment_id', '=', shipments[0].id),
            ('state', 'in', ['done', 'closed'])
        ]).sorted(
            key=lambda trav: trav.date_end_real, reverse=True)

        if not travels:
            return

        self.customer_delivery_date = travels[0].date_end_real.date()
        return

    dealer_id = fields.Many2one(
        'res.partner',
        string="Comerciante",
    )

    partner_dealer_id = fields.Many2one(
        'res.partner.dealer',
        string='Partner Dealer',
        required=False,
    )

    requires_dealer = fields.Boolean(
        string='Requires dealer',
        related="partner_id.requires_dealer"
    )

    shipment_date = fields.Date(
        string='Shipment Date',
    )

    supplier_ref = fields.Char(
        'Supplier Ref',
    )

    customer_delivery_date = fields.Date(
        string='Customer delivery date',
        # compute='_compute_delivery_date',
        # inverse='_set_delivery_date'
    )

    @api.onchange('commitment_date')
    def _onchange_commitment_date(self):
        if not self.commitment_date:
            return

        self.shipment_date = self.commitment_date.date() + relativedelta(days=3)
        return

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        if self.partner_dealer_id:
            invoice_vals['partner_dealer_id'] = self.partner_dealer_id.id
        return invoice_vals

    # @api.one
    # def _set_delivery_date(self):
    #     self.message_post(
    #         body=_('delivery date updated manually.'))
