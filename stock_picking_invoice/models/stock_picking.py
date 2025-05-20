# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    @api.depends('move_ids_without_package')
    def _get_invoice_state(self):
        for pick in self:
            pick.invoice_state = 'none'
            for move in pick.move_ids_without_package:
                if move.invoice_state == 'invoiced':
                    pick.invoice_state = 'invoiced'
                if move.invoice_state == '2binvoiced':
                    pick.invoice_state = '2binvoiced'

    def _set_invoice_state(self):
        for pick in self:
            for move in pick.move_ids_without_package:
                move.invoice_state = pick.invoice_state

    invoice_state = fields.Selection(
        [('invoiced', 'Invoiced'),
         ('2binvoiced', 'To be invoiced'),
         ('none', 'Not Aplicable')],
        string="Invoice control",
        default='none',
        store=True,
        compute='_get_invoice_state',
        inverse='_set_invoice_state',
    )

    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        partner, currency_id, company_id, user_id = key
        payment_type = self.env['ir.model.data'].get_object_reference(
            'cfdi32', 'cfdi_payment_type_010')
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = partner.property_account_receivable_id.id
            payment_term = partner.property_payment_term_id.id or False
            payment_method = partner.payment_method_id or False
            analytic = move.picking_id.sale_id.analytic_account_id
            edi_usage = partner.l10n_mx_edi_usage or False
        else:
            account_id = partner.property_account_payable_id.id
            payment_term = partner.property_supplier_payment_term_id.id \
                or False
            analytic = move.picking_id.purchase_id.account_analytic_id
        if partner.parent_id:
            payment_method = partner.parent_id.payment_method_id
            sales_channel = partner.parent_id.sales_channel_id
            edi_usage = partner.parent_id.l10n_mx_edi_usage
        else:
            payment_method = partner.payment_method_id
            sales_channel = partner.sales_channel_id
            edi_usage = partner.l10n_mx_edi_usage
        return {
            'origin': move.picking_id.name,
            'date_invoice': self._context.get('date_inv', False),
            'user_id': user_id,
            'partner_id': partner.id,
            'partner_shipping_id': move.picking_id.sale_id.
            partner_shipping_id.id,
            'account_id': account_id,
            'payment_term': payment_term,
            'type': inv_type,
            'fiscal_position': partner.property_account_position_id.id,
            'company_id': company_id,
            'currency_id': currency_id,
            'journal_id': journal_id,
            'sale_id': move.picking_id.sale_id.id,
            'account_analytic_id': analytic.id,
            'sales_channel_id': sales_channel.id,
            'payment_method_id': payment_method.id,
            'payment_type_id': payment_type[1],
            'l10n_mx_edi_usage': edi_usage,

        }

    def _create_invoice_from_picking(self, vals):
        '''This function simply creates the invoice from the give values.
        It is overriden in delivery module to add the delivery cost'''
        invoice_obj = self.env['account.invoice']
        return invoice_obj.create(vals)

    def action_invoice_create(self, journal_id, group=False,
                              type='out_invoice'):
        """ Create invoice based on the invoice state selected for picking.
        @param journal_id: Id of  journal_id
        @param group: Whether to creare a group invoice or not
        @param type: Type invoice to be created
        @return: Ids of created invoice for the pickings
        """
        every = {}
        for picking in self.browse(self._context.get('active_ids')):
            partner = picking.partner_id.id
            if group:
                key = partner
            else:
                key = picking.id
            for move in picking.move_ids_without_package:
                if move.invoice_state == '2binvoiced':
                    if (move.state != 'cancel') and not move.scrapped:
                        every.setdefault(key, [])
                        every[key].append(move)
            invoices = []
            for moves in every.values():
                invoices += self._invoive_create_line(moves, journal_id, type)
            return invoices

    def _invoive_create_line(self, moves, journal_id, inv_type='out_invoice'):
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        invoices = {}
        is_extra_move, extra_move_tax = move_obj._get_moves_taxes(moves,
                                                                  inv_type)
        product_price_unit = {}
        for move in moves:
            company = move.company_id
            origin = move.picking_id.name
            partner, user_id, currency_id = move_obj._get_master_data(move,
                                                                      company)

            key = (partner, currency_id, company.id, user_id)
            invoice_vals = self._get_invoice_vals(key, inv_type,
                                                  journal_id, move)

            if key not in invoices:
                invoice_id = self._create_invoice_from_picking(invoice_vals)
                invoices[key] = invoice_id
            else:
                invoice = invoices[key]
                merge_vals = {}
                if not invoice.origin or invoice_vals['origin'] \
                        not in invoice.origin.split(', '):
                    invoice_origin = filter(
                        None, [invoice.origin, invoice_vals['origin']])
                    merge_vals['origin'] = ', '.join(invoice_origin)
                if invoice_vals.get('name', False) and (
                        not invoice.name or invoice_vals['name']
                        not in invoice.name.split(', ')):
                    invoice_name = filter(None, [invoice.name, invoice_vals[
                                          'name']])
                    merge_vals['name'] = ', '.join(invoice_name)
                if merge_vals:
                    invoice.write(merge_vals)

            invoice_line_vals = move_obj._get_invoice_line_vals(move, partner,
                                                                inv_type)
            invoice_line_vals['invoice_id'] = invoices[key].id
            invoice_line_vals['origin'] = origin
            invoice_line_vals['uom_id'] = invoice_line_vals['uos_id']

            if move.picking_id.purchase_id:
                for line in move.picking_id.purchase_id.order_line:
                    if line.product_id.id == invoice_line_vals['product_id']:
                        invoice_line_vals['purchase_line_id'] = line.id
            elif move.picking_id.sale_id:
                for line in move.picking_id.sale_id.order_line:
                    if line.product_id.id == invoice_line_vals['product_id']:
                        invoice_line_vals['sale_line_ids'] = [(
                            6, 0, [line.id])]
            elif inv_type in ('out_refund', 'in_refund'):
                for pick in picking_obj.search(
                        [('name', '=', move.picking_id.origin)]):
                    for line in pick.purchase_id.order_line:
                        if line.product_id.id == invoice_line_vals[
                                'product_id']:
                            invoice_line_vals['purchase_line_id'] = line.id

            if not is_extra_move[move.id]:
                product_price_unit[invoice_line_vals['product_id'],
                                   invoice_line_vals['uos_id']] = \
                    invoice_line_vals['price_unit']
            if is_extra_move[move.id] and (invoice_line_vals['product_id'],
                                           invoice_line_vals['uos_id']) \
                    in product_price_unit:
                invoice_line_vals['price_unit'] = product_price_unit[
                    invoice_line_vals['product_id'], invoice_line_vals[
                        'uos_id']]
            if is_extra_move[move.id]:
                desc = (inv_type in ('out_invoice', 'out_refund') and
                        move.product_id.product_tmpl_id.description_sale) or \
                    (inv_type in ('in_invoice', 'in_refund') and
                     move.product_id.product_tmpl_id.description_purchase)
                invoice_line_vals['name'] += ' ' + desc if desc else ''
                if extra_move_tax[move.picking_id, move.product_id]:
                    invoice_line_vals['invoice_line_tax_id'] = extra_move_tax[
                        move.picking_id, move.product_id]
                elif (0, move.product_id) in extra_move_tax:
                    invoice_line_vals['invoice_line_tax_id'] = extra_move_tax[
                        0, move.product_id]

            move_obj._create_invoice_line_from_vals(move, invoice_line_vals)
            move.invoice_state = 'invoiced'

        # invoice_obj.button_compute()
        return invoices.values()

    def _check_backorder(self):
        """ This method will loop over all the move lines of self and
        check if creating a backorder is necessary. This method is
        called during button_validate if the user has already processed
        some quantities and in the immediate transfer wizard that is
        displayed if the user has not processed any quantities.

        :return: True if a backorder is necessary else False
        """
        quantity_todo = {}
        quantity_done = {}
        for move in self.mapped('move_lines'):
            quantity_todo.setdefault(move.product_id.id, 0)
            quantity_done.setdefault(move.product_id.id, 0)
            quantity_todo[move.product_id.id] += round(move.product_uom_qty, 6)
            quantity_done[move.product_id.id] += round(move.quantity_done, 6)
        for ops in self.mapped('move_line_ids').filtered(lambda x: x.package_id and not x.product_id and not x.move_id):
            for quant in ops.package_id.quant_ids:
                quantity_done.setdefault(quant.product_id.id, 0)
                quantity_done[quant.product_id.id] += round(quant.qty, 6)
        for pack in self.mapped('move_line_ids').filtered(lambda x: x.product_id and not x.move_id):
            quantity_done.setdefault(pack.product_id.id, 0)
            quantity_done[pack.product_id.id] += round(pack.product_uom_id._compute_quantity(pack.qty_done, pack.product_id.uom_id), 6)
        return any(quantity_done[x] < quantity_todo.get(x, 0) for x in quantity_done)
