# Copyright 2023, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import traceback
import logging
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_default_picking_type(self):
        return self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation'),
            ('warehouse_id.company_id', 'in', [self.env.context.get('company_id', self.env.user.company_id.id), False])],
            limit=1).id

    def get_product_cancel_move(self):
        res = {}
        manufacturables = self.get_manufacturables()
        for man in manufacturables:
            if man['bom_type'] == 'phantom':
                continue
            res[man['pp_id']] = man['qty_boms']
        return res

    def get_production_mrp_boost(self):
        self.env.cr.execute("""
            SELECT
                mp.id,
                mp.name,
                mp.product_id,
                mp.product_qty,
                mp.state,
                STRING_AGG(CAST(mpsr2.sale_id AS TEXT), ', ') AS so_ids
            FROM mrp_production_sale_rel AS mpsr
            JOIN mrp_production AS mp ON mpsr.production_id = mp.id
            JOIN mrp_production_sale_rel AS mpsr2 ON mp.id = mpsr2.production_id
            WHERE mpsr.sale_id IN %s
            GROUP BY mp.id
            """, (tuple(self.ids),))

        return self._cr.dictfetchall()

    @api.multi
    def action_closed(self):
        if self.closing_reason is False:
            raise UserError(_("You can't close this Order if you don't"
                              " captured the Closing Reason field!"))
        if self.invoice_status == 'invoiced':
            raise UserError(_("You can't close this Order if you already"
                              " in Billed Status!"))

        productions = self.get_production_mrp_boost()

        for mp in productions:
            if len(mp['so_ids'].split(', ')) == 1:
                if mp['state'] not in ['ready', 'in_production', 'done', 'transfer'] and self.cancel_mo is True:
                    self.env.cr.execute("""
                        UPDATE mrp_production SET state = 'cancel'
                        WHERE id = %s """ % (mp['id']))
                    self.env.cr.execute("""
                        UPDATE stock_move SET state = 'cancel'
                        WHERE state != 'done' AND (raw_material_production_id = %s OR production_id = %s)""", (
                        mp['id'], mp['id']))
            else:
                raise UserError(_("This production order has more than 1 sales order, please notify the administrator"))
        super().action_closed()

    @api.multi
    def action_cancel(self):
        products = self.get_product_cancel_move()
        productions = self.get_production_mrp_boost()

        done_prod = any(item['state'] in [
            'ready', 'in_production', 'done', 'transfer'] for item in productions)
        if done_prod:
            raise UserError(_("The sales order cannot be canceled. Please close it"))
        for mp in productions:
            if len(mp['so_ids'].split(', ')) == 1:
                self.env.cr.execute("""
                    UPDATE mrp_production SET state = 'cancel'
                    WHERE id = %s """ % (mp['id']))
                self.env.cr.execute("""
                    UPDATE stock_move SET state = 'cancel'
                    WHERE state != 'done' AND (raw_material_production_id = %s OR production_id = %s)""", (
                    mp['id'], mp['id']))
            else:
                raise UserError(_("This production order has more than 1 sales order, please notify the administrator"))
                qty_cancel = products[mp['product_id']]
                if round(mp['product_qty'], 6) == round(qty_cancel, 6):
                    self.env.cr.execute("""
                        UPDATE mrp_production SET state = 'cancel'
                        WHERE id = %s """ % (mp['id']))
                    self.env.cr.execute("""
                        UPDATE stock_move SET state = 'cancel'
                        WHERE state != 'done' AND (raw_material_production_id = %s OR production_id = %s)""", (
                        mp['id'], mp['id']))
                else:
                    self.env.cr.execute("""
                        UPDATE mrp_production SET product_qty = product_qty - %s
                        WHERE id = %s
                        """, (qty_cancel, mp['id']))
                    self.env.cr.execute("""
                        UPDATE stock_move SET
                        product_uom_qty = product_uom_qty - ROUND(product_uom_qty / %s * %s, 6),
                        product_qty = product_qty - ROUND(product_qty / %s * %s, 6)
                        WHERE raw_material_production_id = %s OR production_id = %s
                        """, (mp['product_qty'], qty_cancel, mp['product_qty'], qty_cancel,
                              mp['id'], mp['id']))

        super().action_cancel()

    @api.multi
    def validate_alternative(self):
        self.ensure_one()
        not_mo = False

        if not self.is_manufacturer or self.only_customer_delivery:
            not_mo = True
        else:
            self.env.cr.execute("""
                UPDATE sale_order SET only_customer_delivery = True
                WHERE id in (%s) """ % (self.id))

        try:
            self.action_confirm()
        except Exception as error:
            if not not_mo:
                self.env.cr.execute("""
                    UPDATE sale_order SET only_customer_delivery = False
                    WHERE id in (%s) """ % (self.id))
            raise error

        if not_mo:
            return

        manufacturables = self.get_manufacturables()

        res = self.prepare_mo_datas(manufacturables)
        mos = self.create_mos_fromdata(res)
        self.env.cr.execute("""
            UPDATE sale_order SET only_customer_delivery = False
            WHERE id in (%s) """ % (self.id))

    def create_mos_fromdata(self, data=None):
        self._cr.execute("""
            SELECT id FROM procurement_group WHERE sale_id = %s
        """ % self.id)
        procurement_id = self._cr.fetchone()[0]
        for line in data:
            sols = line['sol_ids'].split(", ")
            sos = line['so_ids'].split(", ")
            pars = line['rp_ids'].split(", ")
            self._cr.execute("""
                    INSERT INTO mrp_production(
                    create_uid,create_date,name,
                    product_id,product_qty,product_uom_qty,
                    bom_id,rule_id,user_id,state,
                    origin,company_id,picking_type_id,location_dest_id,
                    availability,write_uid,write_date,
                    product_uom_id, location_src_id,date_planned_start, is_locked,
                    routing_id, procurement_location_id, sale_line_qty_info,
                    procurement_group_id)
                        VALUES(%s,NOW(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),
                            %s, %s,NOW(), true, %s, %s, %s, %s)
                    RETURNING id""", (
                self.env.user.id, line['name'], line['product_id'], line['product_qty'], line['product_qty'],
                line['bom_id'], line['rule_id'], line['user_id'],
                line['status'], line['origin'], line['company_id'],
                line['picking_type_id'], line['location_dest_id'], line['availability'],
                self.env.user.id, line['product_uom_id'], line['location_src_id'],
                line['routing_id'], line['procurement_location_id'],
                line['sale_line_qty_info'], procurement_id))
            mrp = self._cr.fetchone()[0]
            for sol in sols:
                # Insert de la tabla de mo x sols
                self._cr.execute("""
                    INSERT INTO mrp_production_sale_line_rel(production_id,sale_line_id)
                    VALUES (%s,%s)
                    """, (mrp, sol))
            for so in sos:
                # Insert de la tabla de mo x sols
                self._cr.execute("""
                    INSERT INTO mrp_production_sale_rel(production_id,sale_id)
                    VALUES (%s,%s)
                    """, (mrp, so))
            if len(sos) == 1:
                self._cr.execute("""UPDATE mrp_production AS mp SET
                        city_shipping = rp.city,
                        partner_id = so.partner_id,
                        warehouse_id = so.warehouse_id
                    FROM mrp_production_sale_rel AS mpsr
                    JOIN sale_order AS so ON mpsr.sale_id = so.id
                    JOIN res_partner AS rp ON so.partner_shipping_id = rp.id
                    WHERE mp.id = %s AND mp.id = mpsr.production_id
                    """, (mrp,))
            for par in pars:
                # Insert de la tabla de mo x sols
                self._cr.execute("""
                    INSERT INTO mrp_production_partner_rel(production_id,partner_id)
                    VALUES (%s,%s)
                    """, (mrp, par))

            self.create_mos_all_moves(mrp, procurement_id)
            self.create_workorders(mrp)

            self._cr.execute("""UPDATE mrp_production SET state = 'confirmed' WHERE id = %s""", (mrp,))

    def create_workorders(self, mrp=None):
        if not mrp:
            return

        mrp_obj = self.env['mrp.production'].browse([mrp])
        if not mrp_obj or not mrp_obj.routing_id:
            return

        # Would be a good enhance not to write routing_id at all in the M.O.
        # when the rounging has no operations from the very beginning
        if len(mrp_obj.routing_id.operation_ids) == 0:
            self._cr.execute("""
                UPDATE mrp_production
                SET routing_id = %s
                WHERE id = %s
                """, (None, mrp))
            return

        state = 'ready'
        next_id = None
        for line in mrp_obj.routing_id.operation_ids:
            self._cr.execute("""
                INSERT INTO mrp_workorder(
                    create_date,write_date,date_planned_start,production_date,
                    create_uid,write_uid,state,
                    name,production_id,workcenter_id,
                    qty_producing,production_availability,
                    operation_id,product_id,allow_producing_quantity_change,
                    is_first_step,is_last_step,skip_completed_checks,
                    next_work_order_id
                    )
                VALUES(
                    NOW(),NOW(),NOW(),NOW(),
                    %s,%s,%s,
                    %s,%s,%s,
                    %s,%s,
                    %s,%s,True,
                    True,True,False,%s) RETURNING id
                """, (
                self.env.user.id, self.env.user.id, state,
                line.name, mrp_obj.id, line.workcenter_id.id,
                mrp_obj.product_qty, mrp_obj.availability,
                line.id, mrp_obj.product_id.id,
                next_id))
            next_id = self._cr.fetchone()[0]
            state = 'pending'

    def create_mos_all_moves(self, mrp=None, procurement_id=None):
        if not mrp or not procurement_id:
            return

        location_production = self.env.ref('stock.location_production')

        self._cr.execute("""
            INSERT INTO stock_move(
                create_date,date,date_expected,write_date,priority,
                state,propagate,procure_method,additional,
                is_done,to_refund,invoice_state,dev_tipo,

                sequence,bom_line_id,product_id,product_uom,
                price_unit,standard_price,location_id,
                warehouse_id,

                product_uom_qty,product_qty,
                weight,unit_factor,

                create_uid,write_uid,company_id,
                origin,name,reference,
                picking_type_id,raw_material_production_id,
                location_dest_id,scrapped,sale_id, group_id
                )
            SELECT
                NOW(),NOW(),NOW(),NOW(),1,
                'waiting',false,'make_to_stock',false,
                false,false,'none','normal',

                mbl.sequence,mbl.id,mbl.product_id,mbl.product_uom_id,
                ip.value_float,ip.value_float,
                CASE WHEN rc.manufacturing_steps = 1 THEN mbl.location_id ELSE mp.procurement_location_id END,
                sl.stock_warehouse_id,

                ROUND((mp.product_qty/mb.product_qty)*mbl.product_qty,6),
                ROUND((mp.product_qty/mb.product_qty)*mbl.product_qty,6),
                COALESCE(ROUND(((mp.product_qty/mb.product_qty)*mbl.product_qty) * pp.weight,6),0.000000),
                ROUND(((mp.product_qty/mb.product_qty)*mbl.product_qty) / mp.product_qty,6),

                mp.create_uid,mp.create_uid,mp.company_id,
                mp.name,mp.name,mp.name,
                mp.picking_type_id,mp.id,
                %s,%s,%s,%s

            FROM mrp_production AS mp
            JOIN mrp_bom AS mb ON mp.bom_id = mb.id
            JOIN mrp_bom_line AS mbl ON mb.id = mbl.bom_id
            JOIN stock_location AS sl ON mbl.location_id = sl.id
            JOIN product_product AS pp ON mbl.product_id = pp.id
            JOIN res_company AS rc ON mp.company_id = rc.id
            LEFT JOIN ir_property AS ip
                ON CONCAT('product.product,',mbl.product_id) = ip.res_id
                AND ip.name='standard_price'
                AND rc.id = ip.company_id
            WHERE mp.id = %s
            """, (location_production.id,
                  location_production.scrap_location,
                  self.id, procurement_id, mrp))

        self._cr.execute("""
            INSERT INTO stock_move(
                create_date,date,date_expected,write_date,priority,
                state,propagate,procure_method,additional,
                is_done,to_refund,invoice_state,dev_tipo,

                sequence,product_id,product_uom,
                standard_price,location_id,
                warehouse_id,

                product_uom_qty,product_qty,
                weight,

                create_uid,write_uid,company_id,
                origin,name,reference,
                picking_type_id,production_id,
                location_dest_id,scrapped,sale_id,group_id
                )
            SELECT
                NOW(),NOW(),NOW(),NOW(),1,
                'waiting',false,'make_to_stock',false,
                false,false,'none','normal',

                10,mp.product_id,mp.product_uom_id,
                ip.value_float,%s,
                sl.stock_warehouse_id,

                mp.product_qty,mp.product_qty,
                ROUND(mp.product_qty * pp.weight,6),

                mp.create_uid,mp.create_uid,mp.company_id,
                mp.name,mp.name,mp.name,
                mp.picking_type_id,mp.id,
                sl.id,sl.scrap_location,%s,%s

            FROM mrp_production AS mp
            JOIN product_product AS pp ON mp.product_id = pp.id
            JOIN stock_location AS sl ON mp.location_dest_id = sl.id
            LEFT JOIN ir_property AS ip
                ON CONCAT('product.product,',mp.product_id) = ip.res_id
                AND ip.name='standard_price'
                AND mp.company_id = ip.company_id
            WHERE mp.id = %s

            """, (location_production.id, self.id, procurement_id, mrp))

    def prepare_mo_datas(self, manufacturables=None):

        res = []
        for man in manufacturables:
            if man['bom_type'] == 'phantom':
                continue
            picking_type_id = man['pick_type_id'] or self._get_default_picking_type()
            picking_type_id = self.env['stock.picking.type'].browse(picking_type_id)
            if picking_type_id:
                name = picking_type_id.sequence_id.next_by_id()
            else:
                name = self.env['ir.sequence'].next_by_code('mrp.production') or 'New'

            res.append({
                'name': name,
                'product_id': man['pp_id'],
                'product_qty': man['qty_boms'],
                'routing_id': man['routing_id'],
                'bom_id': man['bom_id'],
                'rule_id': man['regla_id'],
                'procurement_location_id': man['procurement_location_id'],
                'user_id': self.env.user.id,
                'tranfer_status': 'not_transferred',
                'status': 'draft',
                'product_uom_id': man['uom_id'],
                'origin': man['names'],
                'company_id': self.env.user.company_id.id,
                'picking_type_id': man['pick_type_id'],
                'location_dest_id': man['location_id'],
                'location_src_id': man['location_mp_id'],
                'availability': 'waiting',
                # 'availability': 'assigned',
                'sale_line_id': False, # This will be a many2many from production.order to sale.order.line
                'sale_id': False, # This will be a many2many from production.order to sale.order.line
                'client_order_ref': False,  # This data will be taken from the above field
                'partner_id': False, # This will be a many2many from production.order to sale.order.line
                'sol_ids': man['sol_ids'],
                'so_ids': man['so_ids'],
                'rp_ids': man['rp_ids'],
                'sale_line_qty_info': man['mp_sol_qty'],
            })
        return res

    def get_manufacturables(self):

        params = [
            self.env.user.id, self.env.user.id, tuple(self.ids),
            self.env.user.id, self.env.user.id, tuple(self.ids),
            tuple(self.ids), self.env.user.id]

        query = """
            WITH RECURSIVE bom_detaill(product_id, pp_id, code, name, qty, bom_id, con, con_bom, route,
                           prod_location, prod_location_id, alm_prod, location, location_id, location_mp_id,
                           almacen, uom_id, pick_type_id, pick_type, regla_id, regla, routing_id, bom_type,
                           procurement_location_id) AS(
                SELECT
                    pp.id,
                    pp.id,
                    pp.default_code,
                    COALESCE(pp.individual_name, pp.name_template, 'Sin definir') AS product,
                    ROUND(mb.product_qty, 6),
                    mb.id,
                    1,
                    CAST(mb.id AS TEXT),
                    slr.name,
                    slmrp.name,
                    slmrp.id,
                    swmrp.name,
                    slpt.name,
                    slpt.id,
                    spit.default_location_src_id,
                    CAST('' AS TEXT),
                    CASE WHEN mb.type = 'normal' THEN mb.product_uom_id ELSE pt.uom_id END,
                    spit.id,
                    spit.name,
                    sru.id,
                    sru.name,
                    mro.id,
                    mb.type,
                    sru.location_id
                    ---,(select count(mrw.id) from mrp_routing_workcenter mrw where mrw.routing_id = mro.id) 
                FROM product_product AS pp
                LEFT JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                JOIN stock_route_product srp ON srp.product_id = pt.id
                JOIN stock_location_route slr ON slr.id = srp.route_id AND
                    (slr.company_id = (SELECT company_id FROM res_users WHERE id = %s))
                     AND slr.name ILIKE ('%%Fabricaci%%')
                LEFT JOIN mrp_bom AS mb ON pp.id = mb.product_id AND mb.active = True
                    AND mb.company_id = (SELECT company_id FROM res_users WHERE id = %s)
                LEFT JOIN mrp_routing mro ON mro.id = mb.routing_id
                    ---AND (select count(mrw.id) from mrp_routing_workcenter mrw where mrw.routing_id = mro.id) > 0
                LEFT JOIN stock_location slmrp ON slmrp.id = mro.location_id
                LEFT JOIN stock_warehouse swmrp ON swmrp.id = slmrp.stock_warehouse_id
                LEFT JOIN stock_location AS slpt ON swmrp.id = slpt.stock_warehouse_id
                    AND slpt.type_stock_loc = 'fp'
                LEFT JOIN stock_picking_type spit ON spit.code = 'mrp_operation'
                    AND spit.warehouse_id = swmrp.id
                LEFT JOIN stock_rule sru ON sru.action = 'manufacture' AND sru.picking_type_id = spit.id
                                           AND sru.location_id = slmrp.id AND sru.route_id = slr.id
                                           AND sru.warehouse_id = swmrp.id
                WHERE pp.id IN (SELECT product_id FROM sale_order_line WHERE order_id IN %s GROUP BY product_id)
                UNION SELECT
                    bd.product_id,
                    pp.id,
                    pp.default_code,
                    COALESCE(pp.individual_name, pp.name_template, 'Sin definir') AS product,
                    ROUND(mbl.product_qty * bd.qty, 6),
                    mb.id,
                    con + 1,
                    CONCAT(bd.con_bom, ' - ' ,CAST(mb.id AS TEXT)),
                    slr.name,
                    slmrp.name,
                    slmrp.id,
                    swmrp.name,
                    sl.name,
                    sl.id,
                    spit.default_location_src_id,
                    swa.name,
                    CASE WHEN mb.type = 'normal' THEN mb.product_uom_id ELSE pt.uom_id END,
                    spit.id,
                    spit.name,
                    sru.id,
                    sru.name,
                    mro.id,
                    mb.type,
                    sru.location_id
                FROM bom_detaill AS bd
                INNER JOIN mrp_bom_line AS mbl ON bd.bom_id = mbl.bom_id
                INNER JOIN product_product AS pp ON mbl.product_id = pp.id
                INNER JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                JOIN stock_route_product srp ON srp.product_id = pt.id
                JOIN stock_location_route slr ON slr.id = srp.route_id AND
                    (slr.company_id = (SELECT company_id FROM res_users WHERE id = %s)) AND slr.name ILIKE ('%%Fabricaci%%')
                LEFT JOIN stock_location AS sl ON mbl.location_id = sl.id
                LEFT JOIN stock_warehouse swa ON swa.id = sl.stock_warehouse_id
                LEFT JOIN mrp_bom AS mb ON pp.id = mb.product_id AND mb.active = True
                    AND mb.company_id = (SELECT company_id FROM res_users WHERE id = %s)
                LEFT JOIN mrp_routing mro ON mro.id = mb.routing_id
                LEFT JOIN stock_location slmrp ON slmrp.id = mro.location_id
                LEFT JOIN stock_warehouse swmrp ON swmrp.id = slmrp.stock_warehouse_id
                LEFT JOIN stock_picking_type spit ON spit.code = 'mrp_operation' AND spit.warehouse_id = swmrp.id
                LEFT JOIN stock_rule sru ON sru.action = 'manufacture' AND sru.picking_type_id = spit.id
                                           AND sru.location_id = slmrp.id AND sru.route_id = slr.id
                                           AND sru.warehouse_id = swmrp.id
            ) /*** Fin del with recursive ***/
            SELECT
                bd.pp_id,
                bd.code,
                bd.prod_location_id,
                bd.prod_location,
                bd.location_id,
                bd.location,
                bd.location_mp_id,
                bd.regla_id,
                bd.regla,
                bd.pick_type_id,
                bd.pick_type,
                bd.bom_id,
                bd.bom_type,
                bd.uom_id,
                bd.routing_id,
                STRING_AGG(DISTINCT CAST(so.id AS TEXT), ', ') AS so_ids,
                STRING_AGG(DISTINCT CAST(rp.id AS TEXT), ', ') AS rp_ids,
                STRING_AGG(DISTINCT CAST(rcsc.id AS TEXT), ', ') AS rcsc_ids,
                STRING_AGG(DISTINCT CAST(rcs.id AS TEXT), ', ') AS rcs_ids,
                STRING_AGG(DISTINCT CAST(sol.id AS TEXT), ', ') AS sol_ids,
                STRING_AGG(DISTINCT CAST(so.week_number AS TEXT), ', ') AS week_numbers,
                STRING_AGG(DISTINCT so.name, ', ') AS names,
                STRING_AGG(DISTINCT CAST(so.date_order AS TEXT), ', ') AS date_orders,
                STRING_AGG(DISTINCT COALESCE(so.client_order_ref, ''), ', ') AS client_order_refs,
                STRING_AGG(DISTINCT mp.name, ', ') AS productions,
                STRING_AGG(DISTINCT pp.default_code, ', ') AS default_codes,
                STRING_AGG(DISTINCT COALESCE(pp.individual_name, pp.name_template, 'Sin definir'), ', ') AS product_es_list,
                SUM(sol.product_uom_qty) AS product_uom_qtys,
                STRING_AGG(DISTINCT CAST(bd.con AS TEXT), ', ') AS cons,
                STRING_AGG(DISTINCT bd.name, ', ') AS name_product_boms,
                SUM((bd.qty * sol.product_uom_qty)) AS qty_boms,
                STRING_AGG(DISTINCT bd_mp.name, ', ') AS production_boms,
                STRING_AGG(DISTINCT bd.route, ', ') AS routes,
                STRING_AGG(DISTINCT bd.alm_prod, ', ') AS alm_prods,
                STRING_AGG(DISTINCT bd.almacen, ', ') AS almacens,
                bd.procurement_location_id,
                STRING_AGG(CAST(sol.id AS TEXT) || ':' || CAST(ROUND(bd.qty * sol.product_uom_qty, 6) AS TEXT), '|') AS mp_sol_qty
            FROM sale_order AS so
            LEFT JOIN res_partner AS rp ON so.partner_id = rp.id
            LEFT JOIN res_partner AS rp_ship ON so.partner_shipping_id = rp_ship.id
            LEFT JOIN res_country_state_city AS rcsc ON rp_ship.city_id = rcsc.id
            LEFT JOIN res_country_state AS rcs ON rp_ship.state_id = rcs.id
            LEFT JOIN sale_order_line AS sol ON so.id = sol.order_id
            LEFT JOIN product_product AS pp ON sol.product_id = pp.id
            LEFT JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
            LEFT JOIN mrp_production AS mp ON pp.id = mp.product_id AND sol.id = mp.sale_line_id
            LEFT JOIN (SELECT * FROM bom_detaill) AS bd ON pp.id = bd.product_id
            LEFT JOIN (SELECT sale_line_id, product_id, product_qty, STRING_AGG(name, ', ') AS name FROM mrp_production 
                WHERE sale_line_id IN (SELECT id FROM sale_order_line WHERE order_id IN %s)
                GROUP BY sale_line_id, product_id, product_qty) AS bd_mp ON bd.pp_id = bd_mp.product_id
                AND sol.id = bd_mp.sale_line_id AND ROUND(bd.qty * sol.product_uom_qty, 6) = ROUND(bd_mp.product_qty, 6)
            WHERE so.id IN %s
                AND so.company_id = (SELECT company_id FROM res_users WHERE id = %s)
                AND sol.product_uom_qty != 0
            GROUP BY bd.pp_id, bd.code, bd.location_id, bd.prod_location, bd.prod_location_id, bd.location, bd.location_mp_id,
                bd.pick_type_id, bd.pick_type, bd.regla_id, bd.regla, bd.bom_id, bd.bom_type, bd.uom_id, bd.routing_id,
                bd.procurement_location_id
        """

        self.env.cr.execute(query, tuple(params))
        return self.env.cr.dictfetchall()

    @api.model
    def force_validate(self):

        pending = self.env['sale.order'].search(
            [('state', 'in', ['draft', 'sent']),
             ('approve', '=', 'approved')], limit=25, order='date_approved')

        for order in pending:
            if not order.company_id.is_manufacturer:
                continue
            try:
                _logger.error(
                    _('Comienza validacion del pedido: %s' % order.name))
                order.validate_alternative()
                self.env.cr.commit()
                _logger.error(
                    _('Termina validacion del pedido: %s' % order.name))
            except Exception:
                self.env.cr.rollback()
                error = tools.ustr(traceback.format_exc())
                _logger.error(
                    _('Error al validar el pedido: %s' % order.name))
                _logger.error(
                    _('Error es: %s' % error))
                continue

        return True


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    production_ids = fields.Many2many(
        'mrp.production',
        'mrp_production_sale_line_rel',
        'sale_line_id',
        'production_id',
        string='Productions',
        copy=False,
    )

    def print_report_tag_sol(self):
        return self.env.ref(
            'sale_order_mrp_boost.tag_sol').report_action(self)

    def action_split_closed_line(self, move, qty):
        if move.product_uom_qty == qty:
            move_canel = move
        else:
            move_canel = move.copy({'product_uom_qty': qty})
            move.write({
                'product_uom_qty': move.product_uom_qty - qty
            })

        self.env.cr.execute("""
            UPDATE stock_move SET state = 'cancel' WHERE id = %s""" % move_canel.id)

    @api.multi
    def action_cancel_generated_moves(self):
        for line in self:
            if not line.order_id.only_customer_delivery:
                continue

            its_us = self.env.user.has_group(
                'system_administrator.group_system_administrator_gebesa')

            if line.auto_purchase_order_line_id and not its_us:
                raise UserError(_(
                    'You cannot close lines from an intercompany Sale Order.'))

            if line.invoice_lines:
                raise UserError(
                    'Esta linea no se puede cerrar, ya esta facturada')

            shiment_line_ids = self.env['mrp.shipment.line'].search([(
                'order_line_id', '=', line.id)])
            if shiment_line_ids:
                raise UserError(
                    'Esta linea no se puede cerrar, ya esta embarcada')

            segment_line_ids = self.env['mrp.segment.line'].search([(
                'mrp_production_id', 'in', line.production_ids.ids), ('state', '!=', 'cancel')])
            if segment_line_ids:
                raise UserError(
                    'Esta linea no se puede cerrar, ya esta segmentada')

            for production in line.production_ids:
                if len(production.sale_order_line_ids) == 1:
                    if production.state in ('draft', 'confirmed'):
                        self._cr.execute("""
                            UPDATE mrp_production AS mp SET state = 'cancel'
                            WHERE mp.id = %s""" % production.id)
                        self.env.cr.execute("""
                            UPDATE stock_move SET state = 'cancel'
                            WHERE state != 'done' AND (raw_material_production_id = %s OR production_id = %s)""", (
                            production.id, production.id))
                    continue
                qty = 0.00
                for sol_data in production.sale_line_qty_info.split('|'):
                    data = sol_data.split(':')
                    if line.id == int(data[0]):
                        qty += float(data[1])

                move_production = production.move_finished_ids.filtered(lambda x: x.state not in ['done','draft','cancel'])

                if move_production.product_uom_qty < qty:
                    raise UserError('La orden de fabricacion %s ya se encuentra en proceso no se puede cancelar' % production.name)

                self.action_split_closed_line(move_production, qty)

                for product in production.move_raw_ids.mapped('product_id'):
                    moves_prod = production.move_raw_ids.filtered(lambda x: x.product_id == product)
                    move_prod = moves_prod.filtered(lambda x: x.state not in ['done','draft','cancel'])
                    qty_product = sum(moves_prod.mapped('product_uom_qty'))
                    qty_cancel = (qty_product / production.product_qty) * qty

                    self.action_split_closed_line(move_prod, qty_cancel)

        super().action_cancel_generated_moves()

    # @api.multi
    # def action_print_generated_move(self):
    #     self.write({'closed': False})
