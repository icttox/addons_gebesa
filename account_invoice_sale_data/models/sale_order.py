# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    geb_invoice_status = fields.Selection(
        [('no_invoice', _('No invoice')),
         ('partial_invoice', _('Partial invoice')),
         ('total_invoice', _(u'Total invoice'))],
        string=_("Invoice status"),
        store=True,
        index=True,
        default='no_invoice',
        compute='_compute_geb_invoice_status'
    )

    @api.depends('order_line.qty_invoiced', 'order_line.product_uom_qty')
    def _compute_geb_invoice_status(self):
        for sale in self:
            if sale.state not in ('done', 'sale'):
                sale.geb_invoice_status = 'no_invoice'
            else:
                qty = 0
                qty_inv = 0
                self._cr.execute("""SELECT geb_invoice_status From sale_order
                                WHERE id = %s""", ([sale.id]))
                if self._cr.rowcount:
                    geb_invoice_status = self._cr.fetchone()[0]
                else:
                    geb_invoice_status = 'no_invoice'
                for line in sale.order_line:
                    if line.product_uom_qty > 0:
                        qty += line.product_uom_qty
                        qty_inv += line.qty_invoiced
                if qty_inv == 0 and not geb_invoice_status:
                    sale.geb_invoice_status = 'no_invoice'
                elif qty_inv < qty and geb_invoice_status == 'no_invoice':
                    sale.geb_invoice_status = 'partial_invoice'
                elif qty_inv == qty:
                    sale.geb_invoice_status = 'total_invoice'
                else:
                    sale.geb_invoice_status = geb_invoice_status

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        portfolio_type = 'national'
        if self.partner_id.country_id.code != self.company_id.country_id.code:
            portfolio_type = 'foreign'
        if self.priority == 'replenishment':
            portfolio_type = 'replacement'
        if self.priority == 'sample':
            portfolio_type = 'sample'
        invoice_vals['portfolio_type'] = portfolio_type
        # if self.partner_dealer_id:
        #     invoice_vals['partner_dealer_id'] = self.partner_dealer_id.id
        return invoice_vals
