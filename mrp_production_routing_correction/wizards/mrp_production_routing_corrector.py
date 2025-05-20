# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpProductionRoutingCorrector(models.TransientModel):
    _name = 'mrp.production.routing.corrector'
    _description = 'descripcion pendiente'

    # routing_id = fields.Many2one(
    #     'mrp.routing',
    #     string='Production Route',
    # )
    location_id = fields.Many2one(
        'stock.location',
        string='Production location',
    )

    @api.multi
    def correct_production_routing(self):
        # mrp_production = 2777, name = MO02783, Origin: 59846:F-ARMA to F-PT
        # mrp_production.move_prod_id

        production_obj = self.env['mrp.production']
        # mrp_prod_line_obj = self.env['mrp.production.product.line']
        move_prod_obj = self.env['stock.move']
        # picking_prod_obj = self.env['stock.picking']
        # quant_obj = self.env['stock.quant']
        active_ids = self._context.get('active_ids', []) or []
        production = production_obj.browse(active_ids)
        # routing_id = self.routing_id
        location_id = self.location_id
        for prod in production.filtered(lambda r: r.state != 'cancel'):
            if prod.state not in ['confirmed', 'planned']:
                if prod.location_src_id.id == location_id.id:
                    for move_dest in prod.move_dest_ids.filtered(
                            lambda r: r.state not in ['done']):
                        move_dest.location_id = location_id.id
                        picking = move_dest.picking_id
                        if picking.location_id.id != location_id.id:
                            if len(picking.move_ids_without_package) > 1:
                                backorder_id = picking.copy({
                                    'name': '/',
                                    'move_ids_without_package': [],
                                    'pack_operation_ids': [],
                                    'backorder_id': picking.id,
                                    'location_id': location_id.id
                                })
                                move_dest.write(
                                    {'picking_id': backorder_id.id})
                            else:
                                picking.location_id = location_id.id
                continue
            # se cambia la ruta y las locaciones del mrp.production
            # prod.routing_id = routing_id.id
            prod.location_src_id = location_id.id
            prod.location_dest_id = location_id.id

            # se modifica el location_id del move_prod_id del mrp.production
            for move_dest in prod.move_dest_ids.filtered(
                    lambda r: r.state not in ['done']):
                # move_prod = prod.move_prod_id
                move_dest.location_id = location_id.id
                if move_dest.picking_id:
                    if move_dest.picking_id.location_id.id != move_dest.location_id.id:
                        if len(move_dest.picking_id.move_ids_without_package) > 1:
                            backorder_id = move_dest.picking_id.copy({
                                'name': '/',
                                'move_ids_without_package': [],
                                'backorder_id': move_dest.picking_id.id,
                                'location_id': move_dest.location_id.id
                            })
                            move_dest.write({'picking_id': backorder_id.id})
                        else:
                            move_dest.picking_id.location_id = location_id.id

            # Busca los positivos para cambiar el location_dest_id
            for move_finish in prod.move_finished_ids.filtered(
                    lambda r: r.state not in ['done']):
                move_finish.location_dest_id = location_id.id

            # Busca los negativos para cambiar el location_id
            move_des = []
            for move_raw in prod.move_raw_ids:
                move_des.extend(move_raw.move_orig_ids.ids)
                if move_raw.state not in ['done']:
                    move_raw.location_id = location_id.id

            # Movimientos que abastecen los productos a consumir
            # para cambiar el location_dest_id
            moves = move_prod_obj.search(
                [('id', 'in', move_des),
                 ('state', 'not in', ['done'])])
            pickings = []
            pick_move = {}
            for mov in moves:
                mov.location_dest_id = location_id.id
                if mov.picking_id not in pickings:
                    pickings.append(mov.picking_id)
                    pick_move[mov.picking_id.id] = []
                pick_move[mov.picking_id.id].append(mov)
            for pick in pickings:
                if pick.location_dest_id.id != location_id.id:
                    if len(pick.move_lines) > len(pick_move[pick.id]):
                        backorder_id = pick.copy({
                            'name': '/',
                            'move_lines': [],
                            'pack_operation_ids': [],
                            'backorder_id': pick.id,
                            'location_dest_id': location_id.id
                        })
                        for pic_mov in pick_move[pick.id]:
                            pic_mov.write({'picking_id': backorder_id.id})
                    else:
                        pick.location_dest_id = location_id.id

        # mrp_production tiene location_src_id igual a la ubicacion
        # donde se fabrica (57) F-ARMA (modi)
        # location_dest_id = la ubicacion donde se fabrica (57) F-ARMA (modi)
        # move_prod_id = 85585

        # Este es el traspaso
        # stock_move = 85585, tiene como move_dest_id = 85584,
        # location_id = 57 (F-ARMA) (modi) tiene procurement_id = 19363,
        # ver si el procurement maneja location_id a modificar
        # picking_id = 1974, location_dest_id = 46 (F-PT)
        # stock_picking = D\INT\00116

        # stock_move, donde production_id = mrp_production.id (85586),
        # es el positivo de la (Actualizacion), del producto a fabricar
        # location_id = 7 (ubicacion virtual de produccion) y location_dest_id =
        # (57) F-ARMA (modi) ubicacion donde se fabrica, move_dest_id = 85585
        # Quere decir que este movimiento fue creado por (85585),
        # tiene procurement_id = 19364

        # Productos a Consumir
        # stock_move donde raw_material_production_id = mrp_production.id es
        # el negativo de las materias primas o productos consumidos
        # de la (Actualizacion) No tiene move_dest_id, location_id = la
        # ubicacion donde se fabrica (57) F-ARMA (modi) y location_dest_id = 7
        # (ubicacion virtual de produccion), no tiene procurement_id
        # "85587", "85589", "85591", "85593", "85595", "85597", "85599"

        # Select stock_move where move_dest_id in ("85587", "85589", "85591",
        # "85593", "85595", "85597", "85599")
        # Movimientos que abastecen los productos a consumir desde otra ubicacion
        # stock_moves generados por los stock_moves anteriores: "85588",
        # "85590", "85592", "85594", "85596", "85598", "85600", tienen
        # location_id = 35, picking_id = 1973, location_dest_id = (57) F-ARMA (modi),
        # No tienen procurement_id, stock_picking = F/OUT/00187

        # mrp_production_product_line tiene location_id = la ubicación donde se fabrica
        # (57) F-ARMA (modi)

        # Los quants de los movimientos modificados.
