# Copyright 2020, César Barrón Bautista
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    # @api.multi
    # def _prepare_invoice(self):
    #     """
    #     Prepare the dict of values to create the new invoice for a sales order. This method may be
    #     overridden to implement custom invoice generation (making sure to call super() to establish
    #     a clean extension chain).
    #     """
    #     res = super(SaleOrder, self)._prepare_invoice()

    #     advance_invoice_id = self.env['account.invoice'].search([
    #         ('sale_id', '=', self.id),
    #         ('prepayment_ok', '=', True),
    #         ('advance_applied', '=', False),
    #         ('state', 'in', ('open', 'paid'))])

    #     if advance_invoice_id:
    #         l10n_mx_edi_origin = '07|'
    #         for advance in advance_invoice_id:
    #             if advance.l10n_mx_edi_cfdi_uuid:
    #                 l10n_mx_edi_origin += advance.l10n_mx_edi_cfdi_uuid + ','
    #         res.update({'advance_id': advance_invoice_id[0].id,
    #                     'amount_advance': advance_invoice_id[0].amount_total,
    #                     'l10n_mx_edi_origin': l10n_mx_edi_origin[:-1]})

    #     return res
