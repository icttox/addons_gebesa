# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    invoice_state = fields.Selection(
        [('invoiced', 'Invoiced'),
         ('2binvoiced', 'To be invoiced'),
         ('none', 'Not Aplicable')],
        string="Invoice control",
        store=True,
        default='none',
    )

    def _get_master_data(self, move, company):
        ''' returns a tuple (browse_record(res.partner), ID(res.users),
        ID(res.currency)'''
        currency = company.currency_id.id
        partner = move.picking_id and move.picking_id.partner_id
        if partner:
            code = self.get_code_from_locs(move)
            if partner.property_product_pricelist and code == 'outgoing':
                currency = partner.property_product_pricelist.currency_id.id
        return partner, self._uid, currency

    def _create_invoice_line_from_vals(self, move, invoice_line_vals):
        return self.env['account.invoice.line'].create(invoice_line_vals)

    def _get_price_unit_invoice(self, move_line, type):
        """ Gets price unit for invoice
        @param move_line: Stock move lines
        @param type: Type of invoice
        @return: The price unit for the move line
        """
        if type in ('in_invoice', 'in_refund'):
            return move_line.price_unit
        # If partner given, search price in its sale pricelist
        if move_line.partner_id and \
                move_line.partner_id.property_product_pricelist:
            pricelist_obj = self.env["product.pricelist"]
            pricelist = move_line.partner_id.property_product_pricelist.id
            price = pricelist_obj.price_get(
                move_line.product_id.id, move_line.product_uom_qty,
                move_line.partner_id.id)[pricelist]
            if price:
                return price
        return move_line.product_id.list_price

    def _get_invoice_line_vals(self, move, partner, inv_type):
        fp_obj = self.env['account.fiscal.position']
        # Get account_id
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = move.product_id.property_account_income_id.id
            analytic = move.picking_id.sale_id.analytic_account_id.id
            if not account_id:
                account_id = move.product_id.categ_id.\
                    property_account_income_categ_id.id
        else:
            account_id = move.product_id.property_account_expense_id.id
            analytic = move.picking_id.purchase_id.account_analytic_id
            if not account_id:
                account_id = move.product_id.categ_id.\
                    property_account_expense_categ_id.id
        account_id = fp_obj.map_account(account_id)

        # set UoS if it's a sale and the picking doesn't have one
        #
        uos_id = move.product_uom.id
        quantity = move.product_uom_qty
        if move.product_uom:
            uos_id = move.product_uom.id
            quantity = move.product_uom_qty

        taxes_ids = self._get_taxes(move)

        return {
            'name': move.name,
            'account_id': account_id,
            'product_id': move.product_id.id,
            'uos_id': uos_id,
            'quantity': quantity,
            'price_unit': self._get_price_unit_invoice(move, inv_type),
            'invoice_line_tax_ids': [(6, 0, taxes_ids)],
            'discount': 0.0,
            'account_analytic_id': analytic.id,
        }

    def _get_moves_taxes(self, moves, inv_type):
        # extra moves with the same picking_id and
        # product_id of a move have the same taxes
        extra_move_tax = {}
        is_extra_move = {}
        for move in moves:
            if move.picking_id:
                is_extra_move[move.id] = True
                if (move.picking_id, move.product_id) not in extra_move_tax:
                    extra_move_tax[move.picking_id, move.product_id] = 0
            else:
                is_extra_move[move.id] = False
        return (is_extra_move, extra_move_tax)

    def _get_taxes(self, move):
        if move.procurement_id.sale_line_id.tax_id:
            return [tax.id for tax in move.procurement_id.sale_line_id.tax_id]
        if move.origin_returned_move_id.purchase_line_id.taxes_id:
            return [tax.id for tax in move.origin_returned_move_id.
                    purchase_line_id.taxes_id]
        return []
