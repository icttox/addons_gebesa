# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# from datetime import datetime
# from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
# from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
# from odoo.tools.translate import _
# from odoo.tools.float_utils import float_is_zero, float_compare
# import openerp.addons.decimal_precision as dp
# from odoo.exceptions import UserError, AccessError
from odoo.osv import osv


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'
    _name = 'procurement.order'

    po_pending = fields.Boolean(
        string=_('PO pending'),
        default=False
    )

    @api.model
    def _run(self, procurement):
        if procurement.rule_id and procurement.rule_id.action == 'buy':
            if procurement.company_id.is_manufacturer:
                if not procurement.po_pending:
                    procurement.write({'po_pending': True})
                    return False
        return super()._run(procurement)

    @api.model
    def run_make_po(self):
        procurements = self.search([('state', '=', 'exception'),
                                    ('po_pending', '=', True)])
        for procurement in procurements:
            procurement.run()
            if procurement.state != 'exception':
                procurement.write({'po_pending': False})

    @api.multi
    def make_po(self):
        cache = {}
        res = []
        for procurement in self:
            suppliers = procurement.product_id.seller_ids.filtered(
                lambda r: not r.product_id or r.product_id == procurement.product_id)
            if not suppliers:
                procurement.message_post(
                    body=_(
                        'No vendor associated to product %s. Please set one to '
                        'fix this procurement.') % (procurement.product_id.name))
                continue
            supplier = suppliers[0]
            partner = supplier.name

            gpo = procurement.rule_id.group_propagation_option
            group = (gpo == 'fixed' and procurement.rule_id.group_id) or \
                    (gpo == 'propagate' and procurement.group_id) or False

            domain = (
                ('partner_id', '=', partner.id),
                ('review', '=', 'no_review'),
                ('state', '=', 'draft'),
                ('picking_type_id', '=', procurement.rule_id.picking_type_id.id),
                ('company_id', '=', procurement.company_id.id),
                ('create_uid', '=', procurement.create_uid.id),
                # ('origin', '=', procurement.origin), # do not group diferent proc's origins
                ('dest_address_id', '=', procurement.partner_dest_id.id))
            if group:
                domain += (('group_id', '=', group.id),)

            if domain in cache:
                po = cache[domain]
            else:
                po = self.env['purchase.order'].search([dom for dom in domain])
                po = po[0] if po else False
                cache[domain] = po
            if not po:
                vals = procurement._prepare_purchase_order(partner)
                po = self.env['purchase.order'].create(vals)
                cache[domain] = po
            elif not po.origin or procurement.origin not in po.origin.split(', '):
                # Keep track of all procurements
                if po.origin:
                    if procurement.origin:
                        po.write({'origin': po.origin + ', ' + procurement.origin})
                    else:
                        po.write({'origin': po.origin})
                else:
                    po.write({'origin': procurement.origin})
            if po:
                res += [procurement.id]

            # Create Line
            po_line = False
            for line in po.order_line:
                if line.product_id == procurement.product_id and line.product_uom == procurement.product_id.uom_po_id:
                    procurement_uom_po_qty = self.env['uom.uom']._compute_qty_obj(procurement.product_uom, procurement.product_qty, procurement.product_id.uom_po_id)
                    seller = self.product_id._select_seller(
                        procurement.product_id,
                        partner_id=partner,
                        quantity=line.product_qty + procurement_uom_po_qty,
                        date=po.date_order and po.date_order[:10],
                        uom_id=procurement.product_id.uom_po_id)

                    price_unit = self.env['account.tax']._fix_tax_included_price(seller.price, line.product_id.supplier_taxes_id, line.taxes_id) if seller else 0.0
                    if price_unit and seller and po.currency_id and seller.currency_id != po.currency_id:
                        price_unit = seller.currency_id.compute(price_unit, po.currency_id)

                    po_line = line.write({
                        'product_qty': line.product_qty + procurement_uom_po_qty,
                        'price_unit': price_unit,
                        'procurement_ids': [(4, procurement.id)]
                    })
                    break
            if not po_line:
                vals = procurement._prepare_purchase_order_line(po, supplier)
                self.env['purchase.order.line'].create(vals)
        return res


class stock_move(osv.osv):
    _inherit = "stock.move"
    _name = "stock.move"

    @api.cr_uid_ids_context
    def _picking_assign(self, cr, uid, move_ids, context=None):
        """Try to assign the moves to an existing picking
        that has not been reserved yet and has the same
        procurement group, locations and picking type  (moves should already
                                                        have them identical)
         Otherwise, create a new picking to assign them to.
        """
        move = self.browse(cr, uid, move_ids, context=context)[0]
        pick_obj = self.pool.get("stock.picking")
        picks = pick_obj.search(
            cr, uid, [
                ('group_id', '=', move.group_id.id),
                ('location_id', '=', move.location_id.id),
                ('location_dest_id', '=', move.location_dest_id.id),
                ('picking_type_id', '=', move.picking_type_id.id),
                ('origin', '=', move.origin),
                ('printed', '=', False),
                ('state', 'in', [
                    'draft',
                    'confirmed',
                    'waiting',
                    'partially_available',
                    'assigned'])], limit=1, context=context)
        if picks:
            pick = picks[0]
        else:
            values = self._prepare_picking_assign(
                cr, uid, move, context=context)
            pick = pick_obj.create(cr, uid, values, context=context)
        return self.write(
            cr, uid, move_ids, {'picking_id': pick}, context=context)
