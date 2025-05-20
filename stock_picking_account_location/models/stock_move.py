# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# from odoo import _, api, fields, models
import logging
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_view_fifo_distribution(self):
        action = self.env.ref(
            'stock_picking_account_location.view_stock_move_fifo_dist_action').read()[0]
        action['domain'] = [('move_id', '=', self.ids)]
        return action

    def _is_in(self):
        """ Check if the move should be considered as entering the company so that the cost method
        will be able to apply the correct logic.

        :return: True if the move is entering the company else False
        """
        for move_line in self.move_line_ids.filtered(lambda ml: not ml.owner_id):
            location_id = move_line.location_id
            location_dest_id = move_line.location_dest_id
            if not location_id._should_be_valued() and location_dest_id._should_be_valued():
                return True
            if location_id.usage == 'internal' and location_dest_id.usage == 'internal' and (
                    location_id.stock_warehouse_id.id != location_dest_id.stock_warehouse_id.id or
                    location_id.type_stock_loc != location_dest_id.type_stock_loc):
                return True
        return False

    def _run_valuation(self, quantity=None):
        self.ensure_one()
        value_to_return = 0
        if self.location_id.usage == 'internal' and self.location_dest_id.usage == 'internal':
            valued_move_lines = self.move_line_ids
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, self.product_id.uom_id)

            # Note: we always compute the fifo `remaining_value` and `remaining_qty` fields no
            # matter which cost method is set, to ease the switching of cost method.
            vals = {}
            price_unit = self._get_price_unit()
            value = price_unit * (quantity or valued_quantity)
            value_to_return = value if quantity is None or not self.value else self.value
            vals = {
                'price_unit': price_unit,
                'value': value_to_return,
                'remaining_value': value if quantity is None else self.remaining_value + value,
            }
            vals['remaining_qty'] = valued_quantity if quantity is None else self.remaining_qty + quantity

            if self.product_id.cost_method == 'standard':
                value = self.product_id.standard_price * (quantity or valued_quantity)
                value_to_return = value if quantity is None or not self.value else self.value
                vals.update({
                    'price_unit': self.product_id.standard_price,
                    'value': value_to_return,
                })
            # Para el caso de Gebesa LLC que se hacen traspasos de un almacen a otro
            # Pero el metodo de costeo es FIFO, productos que no han salido de alguna
            # Ubicacion de Gebesa LLC aunque tenga entradas no tiene costo
            # Por eso se corre el FIFO.
            # De cualquier manera no funciona, ya que ambas ubicaciones origen y destino
            # tienen la propiedad _should_be_valued, para que el fifo funcione una de las
            # dos ubicaciones no lo debe de tener
            if self.product_id.cost_method == 'fifo' and price_unit == 0 and\
                    self.location_id.stock_warehouse_id != self.location_dest_id.stock_warehouse_id:
                self.env['stock.move']._run_fifo(self, quantity=quantity)
            self.write(vals)
            return value_to_return
        return super()._run_valuation(quantity=quantity)

    @api.multi
    def _get_accounting_data_for_valuation(self):
        """ Return the accounts and journal to use to post Journal Entries for
        the real-time valuation of the quant. """
        self.ensure_one()
        accounts_data = self.product_id.product_tmpl_id.get_product_accounts()

        if self.location_id.valuation_out_account_id:
            acc_src = self.location_id.valuation_out_account_id.id
        else:
            acc_src = accounts_data['stock_input'].id

        if self.location_dest_id.valuation_in_account_id:
            acc_dest = self.location_dest_id.valuation_in_account_id.id
        else:
            acc_dest = accounts_data['stock_output'].id

        # Cesar Barron 09 Ago 2016 ##########
        # acc_valuation = accounts.get('stock_valuation', False)
        pick_type = self.picking_id.picking_type_id.code or False

        if pick_type:
            if pick_type == 'incoming':
                if self.location_id.usage == 'customer':
                    acc_dest = self.location_id.account_id.id or False
                acc_valuation = self.location_dest_id.account_id or False
            elif pick_type == 'outgoing':
                acc_valuation = self.location_id.account_id or False
                acc_dest = self.location_dest_id.account_id.id or False
                if self.location_dest_id.usage == 'supplier':
                    acc_src = self.location_dest_id.account_id.id
                if self.location_id.usage not in (
                        'internal', 'transit', 'customer') and \
                        self.location_dest_id.usage == 'internal':
                    acc_src = acc_valuation.id
                    acc_valuation = self.location_dest_id.account_id
            elif pick_type == 'internal':
                if self.location_id.type_stock_loc in ('rm', 'fp'):
                    acc_valuation = self.location_id.account_id or False
                else:
                    acc_valuation = self.location_dest_id.account_id or False
            else:
                acc_valuation = self.location_id.account_id or False
        else:
            if self.location_id.usage == 'internal':
                acc_valuation = self.location_id.account_id or False
            else:
                acc_valuation = self.location_dest_id.account_id or False

        if self.picking_id.stock_move_type_id:
            move_type = self.picking_id.stock_move_type_id.code
            adjustment = self.picking_id.type_adjustment_id
            if move_type in ('E4', 'S4') and not adjustment:
                raise UserError(_('Specify an adjustment type'))
            if move_type == 'E4':
                acc_src = adjustment.account_id.id
            if move_type == 'S4':
                acc_dest = adjustment.account_id.id

        if self.inventory_id:
            if self.location_dest_id.usage == 'inventory':
                acc_valuation = self.location_id.account_id or False
                acc_dest = self.location_dest_id.account_id.id or False
            else:
                acc_valuation = self.location_dest_id.account_id or False
                acc_dest = self.location_id.account_id.id or False

        if not acc_valuation:
            acc_valuation = accounts_data.get('stock_valuation', False)

        # Cesar Barron 09 Ago 2016 ##########

        # Galbo refacciones a taller
        if self.location_id.company_id and not self.location_id.company_id.is_manufacturer and self.location_dest_id.usage == 'production':
            acc_dest = accounts_data.get('expense', False)
            if acc_dest:
                acc_dest = acc_dest.id
        # Galbo refacciones a taller

        if acc_valuation:
            acc_valuation = acc_valuation.id
        if not accounts_data.get('stock_journal', False):
            raise UserError(_('You don\'t have any stock journal defined on your product category, check if you have installed a chart of accounts'))
        if not acc_src:
            raise UserError(_('Cannot find a stock input account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (self.product_id.display_name))
        if not acc_dest:
            raise UserError(_('Cannot find a stock output account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (self.product_id.display_name))
        if not acc_valuation:
            raise UserError(_('You don\'t have any stock valuation account defined on your product category. You must define one before processing this operation.'))
        journal_id = accounts_data['stock_journal'].id
        return journal_id, acc_src, acc_dest, acc_valuation

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id):
        """
        Generate the account.move.line values to post to track the stock
        valuation difference due to the processing of the given quant.
        """

        # _logger.error("Entrando a prepare account move line")

        # _logger.error("Picking id %s" % self.picking_id.id)

        # _logger.error(
        #     "qty: %s cost %s credit_account_id %s .debit_account_id %s" % (
        #         str(qty),
        #         str(cost),
        #         str(credit_account_id),
        #         str(debit_account_id)))
        self.ensure_one()

        if self._context.get('force_valuation_amount'):
            valuation_amount = self._context.get('force_valuation_amount')
            # _logger.error(
            #     "force valuation: %s" % str(valuation_amount))
        else:
            valuation_amount = cost
            # _logger.error(
            #     "cost: %s " % str(valuation_amount))

        # if self._context.get('forced_ref'):
        #     ref = self._context['forced_ref']
        # else:
        #     ref = self.picking_id.name

        # the standard_price of the product may be in another decimal
        # precision, or not compatible with the coinage of
        # the company currency... so we need to use round() before
        # creating the accounting entries.
        debit_value = self.company_id.currency_id.round(valuation_amount)

        # _logger.error(
        #     "debit_value: %s " % str(debit_value))

        # check that all data is correct
        if self.company_id.currency_id.is_zero(debit_value) and not self.env[
                'ir.config_parameter'].sudo().get_param(
                    'stock_account.allow_zero_cost'):
            raise UserError(_(
                "The cost of %s is currently equal to 0. Change the cost or \
                the configuration of your product to avoid an incorrect \
                valuation.") % (self.product_id.display_name,))
        credit_value = debit_value

        partner_id = (self.picking_id.partner_id and self.env[
            'res.partner']._find_accounting_partner(
                self.picking_id.partner_id).id) or False

        # Cesar Barron 09 Ago 2016 ####
        reference = False
        name = False
        # trace = move.location_id.name + "->" + move.location_dest_id.name
        if (self.picking_id and not self.production_id and
                not self.raw_material_production_id):
            reference = self.picking_id.name
            name = self.picking_id.name + " " + self.name
        elif self.production_id:
            reference = self.production_id.name
            name = self.name + \
                ' [' + self.product_id.default_code + '] ' + \
                self.product_id.name
        elif self.raw_material_production_id:
            reference = self.raw_material_production_id.name
            name = self.name + \
                ' [' + self.product_id.default_code + '] ' + \
                self.product_id.name
        elif self.inventory_id:
            reference = self.name
            name = self.name + \
                ' [' + self.product_id.default_code + '] ' + \
                self.product_id.name
        else:
            reference = "W/O Reference "
            name = self.product_id.name
            # + trace
        analytic_id = self.location_id.account_analytic_id.id or False
        if not analytic_id:
            analytic_id = self.location_dest_id.account_analytic_id.id or False

        force_vehicle_analytic_id = False
        if self._context.get('force_vehicle_analytic_id'):
            valuation_amount = self._context.get('force_vehicle_analytic_id')

        analytic_backup_id = False
        if self.location_dest_id.usage == 'internal' and force_vehicle_analytic_id:
            analytic_backup_id = analytic_id
            analytic_id = force_vehicle_analytic_id

        # Cesar Barron 09 Ago 2016 ####

        credit_line_vals = {
            # 'name': self.name,
            'name': name,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            # 'ref': ref,
            'ref': reference,
            'analytic_account_id': analytic_id,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': credit_account_id,
        }

        if analytic_backup_id:
            analytic_id = analytic_backup_id
        if self.location_id.usage == 'internal' and force_vehicle_analytic_id:
            analytic_id = force_vehicle_analytic_id.get('force_vehicle_analytic_id')
        else:
            if self.location_id.usage == 'internal' and self.location_dest_id.usage == 'internal' and self.location_id.stock_warehouse_id.id != self.location_dest_id.stock_warehouse_id.id:
                analytic_id = self.location_dest_id.account_analytic_id.id or False

        # Galbo refacciones a taller
        if self.picking_id and self.picking_id.vms_order_line and not self.location_id.company_id.is_manufacturer and self.location_dest_id.usage == 'production':
            analytic_id = self.picking_id.vms_order_line.order_id.unit_id.account_analytic_id.id
        # Galbo refacciones a taller

        debit_line_vals = {
            # 'name': self.name,
            'name': name,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            # 'ref': ref,
            'ref': reference,
            'analytic_account_id': analytic_id,
            'partner_id': partner_id,
            'debit': debit_value if debit_value > 0 else 0,
            'credit': -debit_value if debit_value < 0 else 0,
            'account_id': debit_account_id,
        }

        res = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
        if credit_value != debit_value:
            # for supplier returns of product in average costing method, in anglo saxon mode
            diff_amount = debit_value - credit_value
            price_diff_account = self.product_id.property_account_creditor_price_difference
            if not price_diff_account:
                price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
            if not price_diff_account:
                raise UserError(_('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))
            price_diff_line = {
                # 'name': self.name,
                'name': name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                # 'ref': ref,
                'ref': reference,
                'partner_id': partner_id,
                'credit': diff_amount > 0 and diff_amount or 0,
                'debit': diff_amount < 0 and -diff_amount or 0,
                'account_id': price_diff_account.id,
            }
            res.append((0, 0, price_diff_line))
        return res

    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id):
        self.ensure_one()
        if self.location_id.usage == 'production' and \
                self.location_dest_id.usage == 'production':
            return
        acc_move_obj = self.env['account.move']
        quantity = self.env.context.get('forced_quantity', self.product_qty)
        quantity = quantity if self._is_in() else -1 * quantity

        # Make an informative `ref` on the created account move to
        # differentiate between classic movements,
        # vacuum and edition of past moves.
        if self.picking_id:
            reference = self.picking_id.name or False
        elif self.production_id:
            reference = self.production_id.name or False
        elif self.raw_material_production_id:
            reference = self.raw_material_production_id.name or False
        elif self.inventory_id:
            reference = self.name or False
        else:
            reference = "W/O Reference"

        move_lines = self.with_context(
            forced_ref=reference)._prepare_account_move_line(
            quantity, abs(self.value), credit_account_id, debit_account_id)
        if move_lines:
            date = self._context.get(
                'force_period_date', fields.Date.context_today(self))
            new_account_move = acc_move_obj.create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'ref': reference,
                'stock_move_id': self.id,
            })
            new_account_move.post()

    def stock_move_create_account_entry(self):
        ctx = dict(self._context)
        for move in self:
            if move.state != 'done':
                continue
            if move.account_move_ids:
                continue
            ctx.update({'force_period_date': move.date})
            move.with_context(ctx)._account_entry_move()

    def _account_entry_move(self):
        """ Accounting Valuation Entries """

        # _logger.error("Entrando a prepare account entry move")

        self.ensure_one()
        if self.product_id.type != 'product':
            # no stock valuation for consumable products
            return False
        if self.restrict_partner_id:
            # if the move isn't owned by the company, we don't make any valuation
            return False

        location_from = self.location_id
        location_to = self.location_dest_id
        company_from = self._is_out() and self.mapped('move_line_ids.location_id.company_id') or False
        company_to = self._is_in() and self.mapped('move_line_ids.location_dest_id.company_id') or False

        # _logger.error(
        #     "location from %s and location to %s." % (location_from.name, location_to.name))

        # Create Journal Entry for products arriving in the company; in case of routes making the link between several
        # warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries
        # if self._is_in():
        if company_to and (self.location_id.usage not in ('internal') and
                           self.location_dest_id.usage == 'internal'):
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
            if location_from and location_from.usage == 'customer':
                # goods returned from customer
                #_logger.error("Case one")
                self.with_context(
                    force_company=company_to.id)._create_account_move_line(
                    acc_dest, acc_valuation, journal_id)
            else:
                #_logger.error("Case two")
                self.with_context(
                    force_company=company_to.id)._create_account_move_line(
                    acc_src, acc_valuation, journal_id)

        # Create Journal Entry for products leaving the company
        # if self._is_out():
        if company_from and (self.location_id.usage == 'internal' and
                             self.location_dest_id.usage not in ('internal')):
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
            if location_to and location_to.usage == 'supplier':
                # goods returned to supplier
                #_logger.error("Case three")
                self.with_context(
                    force_company=company_from.id)._create_account_move_line(
                    acc_valuation, acc_src, journal_id)
            else:
                #_logger.error("Case four")
                self.with_context(
                    force_company=company_from.id)._create_account_move_line(
                    acc_valuation, acc_dest, journal_id)

        # if self.company_id.anglo_saxon_accounting:
        if self.company_id.anglo_saxon_accounting and \
                self.location_id.usage == 'supplier' and \
                self.location_dest_id.usage == 'customer':
            # Creates an account entry from stock_input to stock_output on
            # a dropship move. https://github.com/odoo/odoo/issues/12687
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
            # if self._is_dropshipped():
            #     self.with_context(
            #         force_company=self.company_id.id)._create_account_move_line(
            #         acc_src, acc_dest, journal_id)
            # elif self._is_dropshipped_returned():
            #     self.with_context(
            #         force_company=self.company_id.id)._create_account_move_line(
            #         acc_dest, acc_src, journal_id)
            #_logger.error("Case five")
            self.with_context(
                force_company=self.company_id.id)._create_account_move_line(
                acc_src, acc_dest, journal_id)

        if (self.location_id.usage == 'internal' and
            self.location_dest_id.usage == 'internal' and (
                self.location_id.stock_warehouse_id.id != self.location_dest_id.stock_warehouse_id.id or
                self.location_id.type_stock_loc != self.location_dest_id.type_stock_loc)):
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
            #_logger.error("Case six")
            self.with_context(
                force_company=self.company_id.id)._create_account_move_line(
                acc_src, acc_dest, journal_id)

    @api.model
    def _run_fifo(self, move, quantity=None):
        """ Value `move` according to the FIFO rule, meaning we consume the
        oldest receipt first. Candidates receipts are marked consumed or free
        thanks to their `remaining_qty` and `remaining_value` fields.
        By definition, `move` should be an outgoing stock move.

        :param quantity: quantity to value instead of `move.product_qty`
        :returns: valued amount in absolute
        """
        move.ensure_one()

        before_price_unit = move.price_unit

        # Deal with possible move lines that do not impact the valuation.
        valued_move_lines = move.move_line_ids.filtered(lambda ml: ml.location_id._should_be_valued() and not ml.location_dest_id._should_be_valued() and not ml.owner_id)
        move_line = move.move_line_ids.filtered(lambda ml: ml.location_id._should_be_valued() and ml.location_dest_id._should_be_valued())
        if not self.env.user.company_id.is_manufacturer and move_line:
            raise UserError(_(
                "No se puede hacer un traspaso de una ubicacion fisica a otra, por favor de usar la ubicacion de inventario perdido"))

        valued_quantity = 0
        for valued_move_line in valued_move_lines:
            valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)

        # Find back incoming stock moves (called candidates here) to value this move.
        qty_to_take_on_candidates = quantity or valued_quantity
        candidates = move.product_id._get_fifo_candidates_in_move_with_company(move.company_id.id)
        candidates_location = candidates.filtered(lambda ml: ml.location_dest_id == move.location_id)
        if candidates_location:
            candidates = candidates_location + (candidates - candidates_location)
        new_standard_price = 0
        tmp_qty = 0
        tmp_value = 0  # to accumulate the value taken on the candidates
        for candidate in candidates:
            new_standard_price = candidate.price_unit
            if candidate.remaining_qty <= qty_to_take_on_candidates:
                qty_taken_on_candidate = candidate.remaining_qty
            else:
                qty_taken_on_candidate = qty_to_take_on_candidates

            # As applying a landed cost do not update the unit price, naivelly doing
            # something like qty_taken_on_candidate * candidate.price_unit won't make
            # the additional value brought by the landed cost go away.
            candidate_price_unit = candidate.remaining_value / candidate.remaining_qty
            value_taken_on_candidate = qty_taken_on_candidate * candidate_price_unit
            candidate_vals = {
                'remaining_qty': candidate.remaining_qty - qty_taken_on_candidate,
                'remaining_value': candidate.remaining_value - value_taken_on_candidate,
            }
            candidate.write(candidate_vals)

            qty_to_take_on_candidates -= qty_taken_on_candidate
            tmp_qty += qty_taken_on_candidate
            tmp_value += value_taken_on_candidate

            distribuion = self.env['stock.move.fifo.distribution'].create({
                'move_id': move.id,
                'candidate_id': candidate.id,
                'value_taken_on_candidate': value_taken_on_candidate,
                'qty_taken_on_candidate': qty_taken_on_candidate,
                'candidate_price_unit': candidate_price_unit,
            })

            if qty_to_take_on_candidates == 0:
                break

        # Update the standard price with the price of the last used candidate, if any.
        if new_standard_price and move.product_id.cost_method == 'fifo':
            move.product_id.sudo().with_context(force_company=move.company_id.id) \
                .standard_price = new_standard_price

        # If there's still quantity to value but we're out of candidates, we fall in the
        # negative stock use case. We chose to value the out move at the price of the
        # last out and a correction entry will be made once `_fifo_vacuum` is called.
        if round(qty_to_take_on_candidates, 6) == 0:
            # If the move is not valued yet we compute the price_unit based on the value taken on
            # the candidates.
            # If the move has already been valued, it means that we editing the qty_done on the
            # move. In this case, the price_unit computation should take into account the quantity
            # already valued and the new quantity taken.
            if not move.value:
                price_unit = -tmp_value / (move.product_qty or quantity)
            else:
                price_unit = (-(tmp_value) + move.value) / (tmp_qty + move.product_qty)
            move.write({
                'value': -tmp_value if not quantity else move.value or -tmp_value,  # outgoing move are valued negatively
                'price_unit': price_unit,
            })

            # if move.picking_id and abs((round(price_unit, 2)) != abs(round(before_price_unit, 2))):
            #     move.picking_id.message_post(
            #         body=_('Run FIFO Previous price unit: %d, New price unit: %s. tmp_value: %s, product_qty: %s, quantity: %s, move_value: %s, tmp_qty: %s') % (
            #             before_price_unit, price_unit, tmp_value, move.product_qty, quantity, move.value, tmp_qty))
        elif round(qty_to_take_on_candidates, 6) > 0:
            last_fifo_price = new_standard_price or move.product_id.standard_price
            negative_stock_value = last_fifo_price * -qty_to_take_on_candidates
            tmp_value += abs(negative_stock_value)
            vals = {
                'remaining_qty': move.remaining_qty + -qty_to_take_on_candidates,
                'remaining_value': move.remaining_value + negative_stock_value,
                'value': -tmp_value,
                'price_unit': -1 * last_fifo_price,
            }
            move.write(vals)
            if move.picking_id and abs((round(last_fifo_price, 2)) != abs(round(before_price_unit, 2))):
                move.picking_id.message_post(
                    body=_('Run FIFO New price unit: %d, Previous unit: %s.') % (
                        last_fifo_price, before_price_unit))
        return tmp_value


class StockMoveFifoDistribution(models.Model):
    _name = 'stock.move.fifo.distribution'
    _description = "Temporary implementation for audit propouses"

    product_id = fields.Many2one(
        'product.product',
        related='move_id.product_id',
        string='Product',
    )

    picking_id = fields.Many2one(
        'stock.picking',
        related='move_id.picking_id',
        string='Picking',
    )

    move_id = fields.Many2one(
        'stock.move',
        string='Actual stock move',
        required=True
    )

    candidate_id = fields.Many2one(
        'stock.move',
        string='Candidate',
        required=True,
    )

    qty_taken_on_candidate = fields.Float(
        string='Qty take on candidate',
    )

    value_taken_on_candidate = fields.Float(
        string='Value taken on candidate',
    )

    candidate_price_unit = fields.Float(
        string='Candidate price unit',
    )
