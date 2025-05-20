# -*- coding: utf-8 -*-
# © 2017 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class AccountMoveBomChange(models.TransientModel):
    _name = 'account.move.bom.change'
    _description = u'Generates massive acount moves for changes in BoM'

    date_ini = fields.Date(
        string='Initial date',
        default=fields.Date.today,
    )

    date_end = fields.Date(
        string='Final date',
        default=fields.Date.today,
    )

    @api.multi
    def generate_am_bomchange(self):

        bomhisObj = self.env['mrp.bom.detail.history']
        locationObj = self.env['stock.location']
        stockMoveObj = self.env['stock.move']

        accMoveObj = self.env['account.move']

        for rec in self:
            polizas = accMoveObj.search(
                [('date', '>=', rec.date_ini),
                 ('date', '<=', rec.date_end),
                 ('ref', 'like', 'Standard Price changed ['),
                 ('journal_id', '=', 5)])

            for pol in polizas:
                pol.button_cancel()
                pol.unlink()

            bomChanges = bomhisObj.search(
                [('create_date', '>=', rec.date_ini),
                 ('create_date', '<=', rec.date_end)])

            validLocations = locationObj.search(
                [('type_stock_loc', 'in', ('rm', 'wip', 'fp')),
                 ('stock_warehouse_id', '!=', False)])

            for bomC in bomChanges:
                for loc in validLocations:
                    movesOutLoc = stockMoveObj.search(
                        [('product_id', '=', bomC.product_master_id.id),
                         ('location_id', '=', loc.id),
                         ('state', '=', 'done'),
                         ('date', '<=', bomC.create_date)
                         ])

                    qtyOut = 0.000000
                    for x in movesOutLoc:
                        qtyOut += x.product_uom_qty

                    movesInLoc = stockMoveObj.search(
                        [('product_id', '=', bomC.product_master_id.id),
                         ('location_dest_id', '=', loc.id),
                         ('state', '=', 'done'),
                         ('date', '<=', bomC.create_date)
                         ])

                    qtyIn = 0.000000
                    for x in movesInLoc:
                        qtyIn += x.product_uom_qty

                    inventory = qtyIn - qtyOut

                    datas = bomC.product_master_id.product_tmpl_id._get_product_accounts()

                    if abs(inventory) > 0.00:
                        # Accounting Entries
                        amount_diff = abs(bomC.deference * inventory)
                        if bomC.deference * inventory > 0:
                            debit_account_id = datas['expense'].id
                            credit_account_id = loc.account_id.id
                        else:
                            debit_account_id = loc.account_id.id
                            credit_account_id = datas['expense'].id

                        lines = [(0, 0, {'name': _(
                                         'Standard Price changed [' +
                                         bomC.product_master_id.default_code +
                                         '] ' + bomC.product_master_id.name +
                                         ' for existing in ' + loc.name),
                                         'account_id': debit_account_id,
                                         'debit': amount_diff,
                                         'credit': 0,
                                         'product_id': bomC.product_master_id.id,
                                         'date_maturity': bomC.action_date,
                                         'analytic_account_id':
                                         loc.account_analytic_id.id
                                         }),
                                 (0, 0, {'name': _(
                                         'Standard Price changed [' +
                                         bomC.product_master_id.default_code +
                                         '] ' + bomC.product_master_id.name +
                                         ' for existing in ' + loc.name),
                                         'account_id': credit_account_id,
                                         'debit': 0,
                                         'credit': amount_diff,
                                         'product_id': bomC.product_master_id.id,
                                         'date_maturity': bomC.action_date,
                                         'analytic_account_id':
                                         loc.account_analytic_id.id
                                         })]
                        move_vals = {
                            'journal_id':
                            bomC.product_master_id.categ_id.property_stock_journal.id,
                            'company_id': loc.company_id.id,
                            'line_ids': lines,
                            'date': bomC.action_date,
                            'ref': 'Standard Price changed [' +
                            bomC.product_master_id.default_code +
                            '] ' + bomC.product_master_id.name +
                            ' for existing in ' + loc.name +
                            ' cambio en valor: ' + str(bomC.deference * -1) +
                            ', existencia: ' + str(inventory),
                        }
                        move = self.env['account.move'].create(move_vals)
                        move.post()

        return True


class AccountMoveStockMove(models.TransientModel):
    _name = 'account.move.stock.move'
    _description = u'Generates massive acount moves for Stock Moves'

    date_ini = fields.Date(
        string='Initial date',
        default=fields.Date.today,
    )

    date_end = fields.Date(
        string='Final date',
        default=fields.Date.today,
    )

    @api.multi
    def generate_am_sm(self):

        stockMoveObj = self.env['stock.move']

        accMoveObj = self.env['account.move']

        for rec in self:
            polizas = accMoveObj.search(
                [('date', '>=', rec.date_ini),
                 ('date', '<=', rec.date_end),
                 ('ref', 'like', 'Stock Move ['),
                 ('journal_id', '=', 5)])

            for pol in polizas:
                pol.button_cancel()
                pol.unlink()

            stMoves = stockMoveObj.search(
                [('date', '>=', rec.date_ini),
                 ('date', '<=', rec.date_end),
                 ('state', '=', 'done')])

            for stmov in stMoves:

                cost = stmov.price_unit or stmov.standard_price or False
                if not cost:
                    cost = stmov.product_id.standard_price

                analytic_out_id = stmov.location_id.account_analytic_id.id or False
                if not analytic_out_id:
                    analytic_out_id = stmov.location_dest_id.account_analytic_id.id or False

                analytic_in_id = stmov.location_dest_id.account_analytic_id.id or False
                if not analytic_in_id:
                    analytic_in_id = stmov.location_id.account_analytic_id.id

                amount = abs(stmov.product_uom_qty * cost)

                partner_id = (
                    stmov.picking_id.partner_id and self.pool.get(
                        'res.partner')._find_accounting_partner(
                            stmov.picking_id.partner_id).id) or False

                reference = ''
                if stmov.picking_id:
                    reference = "Number: " + stmov.picking_id.name
                    if stmov.location_dest_id.usage in [
                            'internal', 'production']:
                        if stmov.location_id.usage == 'customer':
                            reference = '(E1) Devolución de Cliente ' + reference
                        elif stmov.location_id.usage == 'supplier':
                            reference = '(E2) Entrada por compra ' + reference
                        elif stmov.location_id.usage == 'transit':
                            reference = '(E3) Entrada por traspaso ' + reference
                        elif stmov.location_id.usage == 'inventory':
                            reference = '(EA) Entrada por ajuste ' + reference

                    if stmov.location_id.usage in [
                            'internal', 'production']:
                        if stmov.location_dest_id.usage == 'customer':
                            reference = '(S1) Salida por venta ' + reference
                        elif stmov.location_dest_id.usage == 'supplier':
                            reference = '(S2) Devolución a proveedor ' + reference
                        elif stmov.location_dest_id.usage == 'transit':
                            reference = '(S3) Salida por traspaso ' + reference
                        elif stmov.location_dest_id.usage == 'inventory':
                            reference = '(SA) Salida por ajuste ' + reference
                        elif stmov.location_dest_id.usage == 'production':
                            if stmov.location_id.usage == 'internal':
                                reference = '(SB) Salida por abastecimiento ' + reference
                        elif stmov.location_dest_id.usage == 'internal':
                            if stmov.location_id.usage == 'production':
                                reference = '(ST) Salida por traspaso (Fabricación) ' + reference
                            elif stmov.location_id.usage == 'internal' and stmov.location_id.stock_warehouse_id != stmov.location_dest_id.stock_warehouse_id:
                                reference = '(SD) Salida por traspaso (Directa) ' + reference

                elif stmov.production_id:
                    reference = "MO Number: " + stmov.production_id.name
                elif stmov.raw_material_production_id:
                    reference = "MO Number (Consumo): " + stmov.raw_material_production_id.name
                elif stmov.inventory_id:
                    reference = "Inventory number: " + stmov.inventory_id.name

                # if not stmov.location_dest_id.account_id.id:
                #     cuenta = stmov.location_dest_id.account_id.id

                # if not stmov.location_id.account_id.id:
                #     cuenta2 = stmov.location_id.account_id.id

                lines = [(0, 0, {'name': _(
                                 'Stock Move [' +
                                 stmov.product_id.default_code +
                                 '] ' + stmov.product_id.name),
                                 'account_id':
                                 stmov.location_dest_id.account_id.id,
                                 'debit': amount,
                                 'credit': 0,
                                 'quantity': stmov.product_uom_qty,
                                 'product_id': stmov.product_id.id,
                                 'date_maturity': stmov.date,
                                 'ref': reference,
                                 'partner_id': partner_id,
                                 'product_uom_id': stmov.product_id.uom_id.id,
                                 'analytic_account_id': analytic_in_id
                                 }),
                         (0, 0, {'name': _(
                                 'Stock Move [' +
                                 stmov.product_id.default_code +
                                 '] ' + stmov.product_id.name),
                                 'account_id':
                                 stmov.location_id.account_id.id,
                                 'debit': 0,
                                 'credit': amount,
                                 'quantity': stmov.product_uom_qty,
                                 'product_id': stmov.product_id.id,
                                 'date_maturity': stmov.date,
                                 'product_uom_id': stmov.product_id.uom_id.id,
                                 'ref': reference,
                                 'partner_id': partner_id,
                                 'analytic_account_id': analytic_out_id
                                 })]

                move_vals = {
                    'journal_id':
                    stmov.product_id.categ_id.property_stock_journal.id,
                    'company_id': stmov.company_id.id,
                    'line_ids': lines,
                    'date': stmov.date,
                    'ref': reference + ' Stock Move [' +
                    stmov.product_id.default_code +
                    '] ' + stmov.product_id.name,
                }
                move = self.env['account.move'].create(move_vals)
                move.post()

            return True
