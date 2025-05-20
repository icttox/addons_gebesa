# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    closed = fields.Boolean(
        string='Closed',
        default=False,
    )

    # def get_procurement_list(self, procurement_id):
    #     move_obj = self.env['stock.move']
    #     procurement_ids = []
    #     if procurement_id.rule_id.action == 'move':
    #         move_dest_ids = procurement_id.mapped('move_ids').mapped('id')
    #         move_ids = move_obj.search([('move_dest_id', 'in', move_dest_ids)])
    #         procurement_ids.extend(move_ids.mapped('procurement_id').mapped(
    #             'id'))
    #         for procurement in move_ids.mapped('procurement_id'):
    #             procurement_ids.extend(self.get_procurement_list(procurement))
    #     elif procurement_id.rule_id.action == 'manufacture':
    #         move_dest_ids = procurement_id.mapped('production_id').mapped(
    #             'move_lines').mapped('id')
    #         move_ids = move_obj.search([('move_dest_id', 'in', move_dest_ids)])
    #         procurement_ids.extend(move_ids.mapped('procurement_id').mapped(
    #             'id'))
    #         if not procurement_ids:
    #             move_ids = move_obj.search([(
    #                 'move_dest_id', 'in', move_ids.ids)])
    #             procurement_ids.extend(move_ids.mapped(
    #                 'procurement_id').mapped('id'))
    #         for procurement in move_ids.mapped('procurement_id'):
    #             procurement_ids.extend(self.get_procurement_list(procurement))
    #     return procurement_ids

    @api.depends('closed', 'qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state')
    def _get_to_invoice_qty(self):
        """
        Compute the quantity to invoice. If the invoice policy is order, the quantity to invoice is
        calculated from the ordered quantity. Otherwise, the quantity delivered is used.
        """
        for line in self:
            if line.order_id.state in ['sale', 'done'] and not line.closed:
                if line.product_id.invoice_policy == 'order':
                    line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    @api.multi
    def action_print_generated_move(self):
        # self.write({'closed': True})
        return self.env.ref('order_line_cancel.movements_generated_line_item').report_action(self)

    @api.multi
    def action_cancel_generated_moves(self):
        # procurement_obj = self.env['procurement.order']
        shipment_line_obj = self.env['mrp.shipment.line']
        segment_line_obj = self.env['mrp.segment.line']
        production_obj = self.env['mrp.production']
        location_obj = self.env['stock.location']
        moves_obj = self.env['stock.move']

        location_ids = location_obj.search([('usage', '=', 'customer')])
        location_ids = location_ids.mapped('id')

        for line in self:
            # procurement_list = []
            # move_list = []

            its_us = self.env.user.has_group(
                'system_administrator.group_system_administrator_gebesa')

            if line.auto_purchase_order_line_id and not its_us:
                raise ValidationError(_(
                    'You cannot close lines from an intercompany Sale Order.'))

            if line.invoice_lines:
                raise ValidationError(
                    'Esta linea no se puede cerrar, ya esta facturada')

            shiment_line_ids = shipment_line_obj.search([(
                'order_line_id', '=', line.id)])
            if shiment_line_ids:
                raise ValidationError(
                    'Esta linea no se puede cerrar, ya esta embarcada')

            # procurement_id = procurement_obj.search([(
            #     'sale_line_id', '=', line.id)])
            # procurement_list.extend(line.get_procurement_list(procurement_id))
            # procurement_list.append(procurement_id.id)

            # procurement_ids = procurement_obj.search([(
            #     'id', 'in', procurement_list)])
            # production_ids = procurement_ids.mapped(
            #     'production_id').mapped('id')
            # si el segmento esta cancelado no muestre error filtro no consdierar mo canceladas
            production_ids = production_obj.search([(
                'sale_line_id', '=', line.id)]).mapped('id')
            segment_line_ids = segment_line_obj.search([(
                'mrp_production_id', 'in', production_ids), ('state', '!=', 'cancel')])
            if segment_line_ids:
                raise ValidationError(
                    'Esta linea no se puede cerrar, ya esta segmentada')
            # move_list.extend(procurement_ids.mapped('move_ids').mapped('id'))

            # move_list.extend(procurement_ids.mapped('production_id').mapped(
            #     'move_prod_id').mapped('id'))
            # move_list.extend(procurement_ids.mapped('production_id').mapped(
            #     'move_lines').mapped('id'))
            # move_list.extend(procurement_ids.mapped('production_id').mapped(
            #     'move_lines2').mapped('id'))
            # move_list.extend(procurement_ids.mapped('production_id').mapped(
            #     'move_created_ids').mapped('id'))
            # move_list.extend(procurement_ids.mapped('production_id').mapped(
            #     'move_created_ids2').mapped('id'))

            # move_id_list = moves_obj.search([(
            #     'move_dest_id', 'in', move_list)])
            # move_list.extend(move_id_list.mapped('id'))

            move_list = moves_obj.search([(
                'sale_line_id', '=', line.id)]).mapped('id')

            move_ids = moves_obj.search([(
                'id', 'in', move_list), (
                'location_dest_id', 'in', location_ids), (
                'state', '=', 'done')])
            if move_ids:
                raise ValidationError(
                    'Esta linea no se puede cerrar, ya se entrego al cliente')

            if production_ids:
                production_list_str = ', '.join(map(str, production_ids))
                self._cr.execute("""
                    UPDATE mrp_production AS mp
                    SET state = 'cancel'
                    WHERE mp.state IN ('draft', 'confirmed')
                    AND mp.id in (%s)""" % production_list_str)

            move_list_str = ', '.join(map(str, move_list))
            self._cr.execute("""
                UPDATE stock_move AS sm
                SET state = 'cancel'
                FROM (select sm.id, coalesce(mp.state, 'cancel') as status
                    from stock_move as sm
                    left join mrp_production mp on sm.created_production_id = mp.id
                    or sm.production_id = mp.id
                    or sm.raw_material_production_id = mp.id
                    where sm.id in (%s)) as sm_cancel
                WHERE sm.state NOT IN ('assigned', 'done')
                AND sm.id = sm_cancel.id and sm_cancel.status = 'cancel'
            """ % move_list_str)

            # Cancel movelines y desreservar, para stock_moves_cancelados:
            # Asi es, no filtra solo los movimientos de este pedido, es a proposito
            # No deberian ser muchos
            self._cr.execute("""
                UPDATE stock_move_line
                    SET state = 'cancel',
                    product_qty = 0.00000
                FROM stock_move sm
                WHERE sm.id = stock_move_line.move_id
                AND sm.state = 'cancel' AND stock_move_line.state != 'cancel'
            """)

            move_ids = moves_obj.search([('id', 'in', move_list)])
            picking_list = move_ids.mapped('picking_id').mapped('id')
            picking_list_str = ', '.join(map(str, picking_list))

            self._cr.execute("""
                UPDATE stock_picking sp set state = 'cancel'
                from (
                select sp.id, string_agg(distinct(sm.state),', ') as status
                from stock_picking sp
                join stock_move sm on sp.id = sm.picking_id
                where sp.id IN (%s)
                group by sp.id) as sp_cancel
                where sp.id = sp_cancel.id and sp_cancel.status = 'cancel'
            """ % picking_list_str)
            line.write({'closed': True})

            if line.auto_purchase_order_line_id:
                purchase_line = line.sudo().auto_purchase_order_line_id
                message_body = """
                    <b>Linea de pedido multicompany cerrada</b><br/>
                        Producto %s (linea %s) del lado de: %s""" % (
                    line.product_id.default_code, line.id, line.order_id.company_id.name)

                purchase_line.order_id.activity_schedule(
                    'mail.mail_activity_data_warning',
                    date.today(),
                    note=message_body,
                    user_id=purchase_line.sale_line_id.order_id.create_uid.id
                )

                purchase_line.order_id.message_post(body=message_body)

        # Comentariado temporal mente mientras se migran repoertes pentaho
        # ctx = dict(
        #     self.env.context or {},
        #     active_ids=self.ids,
        #     active_model=self._name)
        # return{
        #     'type': 'ir.actions.report.xml',
        #     'report_name': 'movimientos.generados.linea.pedido',
        #     'context': ctx,
        # }
        return self.action_print_generated_move()


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    o_total_net_sale = fields.Float(
        string='Importe',
        digits=dp.get_precision('Account'),
        compute="_compute_fields_sale_order",
        store=True,
    )
    o_total_cost = fields.Float(
        string='Total Cost',
        digits=dp.get_precision('Account'),
        compute="_compute_fields_sale_order",
        store=True,
    )
    o_amount_pending = fields.Float(
        string='Amount Pending',
        digits=dp.get_precision('Account'),
        compute="_compute_fields_sale_order",
        store=True,
    )
    o_profit_margen = fields.Float(
        string='Margin',
        digits=dp.get_precision('Account'),
        compute="_compute_fields_sale_order",
        store=True,
    )
    o_total_freight = fields.Float(
        string='Total Freight',
        digits=dp.get_precision('Account'),
        compute="_compute_fields_sale_order",
        store=True,
    )
    o_total_installation = fields.Float(
        string='Total Installation',
        digits=dp.get_precision('Account'),
        compute="_compute_fields_sale_order",
        store=True,
    )
    o_standard_cost_pending = fields.Float(
        string='Standard cost pending',
        compute="_compute_fields_sale_order",
        store=True,
    )
    o_freight_rate_mex = fields.Float(
        string='Freight rate mex',
        compute="_compute_fields_sale_order",
        store=True,
    )
    o_installation_rate_mex = fields.Float(
        string='Installation rate mex',
        compute="_compute_fields_sale_order",
        store=True,
    )
    o_net_sale_rate_mex = fields.Float(
        string='Net sale rate mex',
        compute="_compute_fields_sale_order",
        store=True,
    )
    o_amount_untaxed = fields.Float(
        string='Amount Untaxed',
        compute="_compute_fields_sale_order",
        store=True,
    )
    o_amount_untaxed_rate_mex = fields.Float(
        string='Amount Untaxed Rate Mex',
        compute="_compute_fields_sale_order",
        store=True,
    )
    o_amount_pending_rate_mex = fields.Float(
        string='Amount Pending Rate Mex',
        digits=dp.get_precision('Account'),
        compute="_compute_fields_sale_order",
        store=True,
    )
    o_volume = fields.Float(
        'Volumen',
        compute='_compute_o_volumen_weight',
        store=True,
    )
    o_weight = fields.Float(
        'Weight',
        compute='_compute_o_volumen_weight',
        store=True,
    )

    @api.depends('order_line', 'order_line.product_uom_qty',
                 'order_line.product_id', 'order_line.closed')
    def _compute_o_volumen_weight(self):
        for order in self:
            order = order.sudo()
            volume = 0.0
            weight = 0.0
            for line in order.order_line:
                if line.closed is not True:
                    volume += (line.product_uom_qty * line.product_id.volume)
                    weight += (line.product_uom_qty * line.product_id.weight)
            order.o_volume = volume
            order.o_weight = weight

    def recalc_weight_volume(self):
        self._cr.execute("""
            UPDATE sale_order AS so SET
                o_volume = t1.volume,
                o_weight = t1.weight
            FROM (SELECT
                so.id,
                ROUND(CAST(SUM(sol.product_uom_qty * pp.volume) AS NUMERIC), 6) AS volume,
                ROUND(CAST(SUM(sol.product_uom_qty * pp.weight) AS NUMERIC), 6) AS weight
            FROM sale_order AS so
            JOIN sale_order_line AS sol ON so.id = sol.order_id
            JOIN product_product AS pp ON sol.product_id = pp.id
            WHERE so.id IN %s
            GROUP BY so.id ) AS t1
            WHERE so.id = t1.id
        """, [tuple(self.ids)])

    @api.depends('order_line', 'order_line.product_id',
                 'order_line.standard_cost', 'order_line.net_sale',
                 'order_line.freight_amount', 'order_line.installation_amount',
                 'order_line.product_uom_qty', 'order_line.pending_qty',
                 'order_line.closed', 'order_line.standard_cost',
                 'rate_mex', 'order_line.price_subtotal')
    def _compute_fields_sale_order(self):
        for order in self:
            global_cost = 0.0
            global_net_sale = 0.0
            global_freight = 0.0
            global_installa = 0.0
            global_profit_margin = 0.0
            global_amount_pending = 0
            global_standard_cost_pending = 0
            global_amount_untaxed = 0.0

            currency = order.company_id.currency_id
            for line in order.order_line:
                if line.closed is not True:
                    global_cost += line.standard_cost
                    global_net_sale += line.net_sale
                    global_freight += line.freight_amount
                    global_installa += line.installation_amount
                    global_amount_untaxed += line.price_subtotal

                    if line.product_uom_qty > 0:
                        global_amount_pending += line.pending_qty * (
                            line.net_sale / line.product_uom_qty)
                        global_standard_cost_pending += line.pending_qty *\
                            (line.standard_cost / line.product_uom_qty)
            if global_net_sale > 0.000000:
                # global_total_pm = currency.compute(
                #     global_cost, order.pricelist_id.currency_id)
                global_total_pm = currency._convert(
                    global_cost, order.pricelist_id.currency_id, order.company_id, fields.Date.today())
                global_profit_margin = (
                    1 - (global_total_pm) / global_net_sale)
                global_profit_margin = global_profit_margin * 100

            order.o_total_cost = global_cost
            order.o_total_net_sale = global_net_sale
            order.o_total_freight = global_freight
            order.o_total_installation = global_installa
            order.o_profit_margen = global_profit_margin
            order.o_amount_pending = global_amount_pending
            order.o_standard_cost_pending = global_standard_cost_pending
            order.o_amount_untaxed = global_amount_untaxed

            if not order.rate_mex:
                order.o_freight_rate_mex = order.o_total_freight
                order.o_installation_rate_mex = order.o_total_installation
                order.o_net_sale_rate_mex = order.o_total_net_sale
                order.o_amount_untaxed_rate_mex = order.o_amount_untaxed
                order.o_amount_pending_rate_mex = order.o_amount_pending
            else:
                order.o_freight_rate_mex = order.rate_mex * order.o_total_freight
                order.o_installation_rate_mex = order.rate_mex * order.o_total_installation
                order.o_net_sale_rate_mex = order.rate_mex * order.o_total_net_sale
                order.o_amount_untaxed_rate_mex = order.rate_mex * order.o_amount_untaxed
                order.o_amount_pending_rate_mex = order.rate_mex * order.o_amount_pending

    @api.depends('order_line.quantity_shipped', 'order_line.product_uom_qty',
                 'order_line.closed')
    def _compuete_shiptment_status(self):
        for sale in self:
            ship_qty = 0
            pro_qty = 0
            # prev_status = sale.shiptment_status
            for line in sale.order_line:
                if line.closed is not True:
                    ship_qty += line.quantity_shipped
                    pro_qty += line.product_uom_qty
            if ship_qty == 0:
                sale.shiptment_status = 'no_shipment'
                # ship_status = 'No shipment'
            elif ship_qty == pro_qty:
                sale.shiptment_status = 'total_shipment'
                # ship_status = 'Total shipment'
            else:
                sale.shiptment_status = 'partial_shipment'
                # ship_status = 'Partial shipment'
            # if prev_status != sale.shiptment_status:
                # sale.message_post(body=_(
                #    "Shipment status <em>%s</em>.") % (
                #    ship_status))

    @api.depends('order_line.segment_qty', 'order_line.closed')
    def _compuete_production_status(self):
        for sale in self:
            seg_qty = 0
            pro_qty = 0
            for line in sale.order_line:
                if line.closed is not True:
                    seg_qty += line.segment_qty
                    pro_qty += line.product_uom_qty
            if seg_qty == pro_qty:
                sale.production_status = 'total_production'
            elif seg_qty == 0:
                sale.production_status = 'no_production'
            else:
                sale.production_status = 'partial_production'

    @api.depends('order_line.qty_invoiced', 'order_line.product_uom_qty',
                 'order_line.closed')
    def _compute_geb_invoice_status(self):
        for sale in self:
            if sale.state not in ('done', 'sale'):
                sale.geb_invoice_status = 'no_invoice'
            else:
                qty = 0
                qty_inv = 0
                try:
                    self._cr.execute("""SELECT geb_invoice_status From sale_order
                                    WHERE id = %s""", ([sale.id]))
                except:
                    continue
                if self._cr.rowcount:
                    geb_invoice_status = self._cr.fetchone()[0]
                else:
                    geb_invoice_status = 'no_invoice'
                for line in sale.order_line:
                    if line.product_uom_qty > 0:
                        if line.closed is not True:
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
