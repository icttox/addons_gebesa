# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class MrpShipment(models.Model):
    _name = 'mrp.shipment'
    _description = 'Shipment'
    _rec_name = 'folio'
    _order = "folio desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection(
        [('draft', 'Draft'),
         ('cancel', 'Cancelled'),
         ('confirm', 'In Progress'),
         ('done', 'Validated'),
         ('finished', 'Finished')],
        string='Status',
        readonly=True,
        index=True,
        default='draft',
        copy=False
    )
    folio = fields.Char(
        string='Folio',
        required=True,
        readonly=True,
        copy=False,
        default='new',
    )
    reference = fields.Text(
        string='Reference',
        required=True,
    )
    date = fields.Date(
        string='Date of shipment',
        default=fields.Date.today
    )
    departure_date = fields.Date(
        string='Departure date',
        default=fields.Date.today
    )
    meters = fields.Float(
        string='Meters',
        compute='_compute_meters'
    )
    freight = fields.Float(
        string='Freight',
        compute='_compute_meters',
        digits=dp.get_precision('Account'),
    )
    weight = fields.Float(
        string='Weight',
        compute='_compute_meters',
    )
    amount = fields.Float(
        string='Amount',
        compute='_compute_meters',
        digits=dp.get_precision('Account'),
    )
    line_ids = fields.One2many(
        'mrp.shipment.line',
        'shipment_id',
        string='Shipment Products',
        readonly=False,
        states={'done': [('readonly', True)]},
        help="Shipment Lines.",
        copy=True
    )
    sale_ids = fields.One2many(
        'mrp.shipment.sale',
        'shipment_id',
        string='Shipment Order',
        readonly=False,
        states={'done': [('readonly', True)]},
        copy=True
    )
    partner_ids = fields.One2many(
        'mrp.shipment.partner',
        'shipment_id',
        string='Shipment Partner',
        compute='_compute_partners',
        readonly=False,
        store=True,
    )

    @api.multi
    def reverse_in_progress(self):
        return self.write({'state': 'confirm'})

    @api.depends('sale_ids', 'sale_ids.partner_id')
    def _compute_partners(self):
        list_partner = []
        for shipment in self:
            list_partner = shipment.mapped('sale_ids').mapped('partner_shipping_id').mapped('id')
            sequence = 0
            partners_obj = self.env['mrp.shipment.partner']
            for list_ in list_partner:
                #import ipdb; ipdb.set_trace()
                data = {
                    'partner_id': list_,
                    #'shipment_id': shipment.id,
                    'sequence': sequence,
                }
                partner = partners_obj.new(data)
                partners_obj += partner
                sequence += 1
            # import ipdb; ipdb.set_trace()
            shipment.partner_ids += partners_obj
        return {}

    @api.depends('line_ids', 'line_ids.quantity_shipped')
    def _compute_meters(self):
        for shipment in self:
            meters = 0
            freight = 0
            amount = 0
            weigh = 0
            for line in shipment.line_ids:
                meters += (line.product_id.volume * line.quantity_shipped)
                weigh += (line.product_id.weight * line.quantity_shipped)
                if line.order_line_id.product_uom_qty > 0:
                    freight += (line.order_line_id.freight_amount /
                                line.order_line_id.product_uom_qty) * \
                        line.quantity_shipped
                    amount += (line.order_line_id.net_sale /
                               line.order_line_id.product_uom_qty) * \
                        line.quantity_shipped
            shipment.meters = meters
            shipment.freight = freight
            shipment.amount = amount
            shipment.weight = weigh

    @api.model
    def create(self, vals):
        if vals.get('folio', 'new') == 'new':
            vals['folio'] = self.env['ir.sequence'].next_by_code(
                'mrp.shipment') or '/'
        return super(MrpShipment, self).create(vals)

    @api.multi
    def unlink(self):
        for shipment in self:
            if shipment.state != 'cancel':
                raise ValidationError(_("You can only delete canceled \
                    shipments"))
        return super(MrpShipment, self).unlink()

    @api.multi
    def write(self, vals):
        res = super(MrpShipment, self).write(vals)
        for ship in self:
            for sale in ship.mapped('line_ids').mapped('sale_order_id').mapped('id'):
                self._cr.execute(
                    """SELECT so.id, so.name
                        FROM pedidos_vinculados_sale_order_rel AS pvsor
                        JOIN pedidos_vinculados AS pv ON pv.id = pvsor.pedidos_vinculados_id
                        JOIN pedidos_vinculados_sale_order_rel AS pvsor2 ON pv.id = pvsor2.pedidos_vinculados_id
                        JOIN sale_order AS so ON so.id = pvsor2.sale_order_id
                        WHERE pv.activo = true AND pvsor.sale_order_id = %s AND pvsor.sale_order_id != so.id""",
                    ([sale]))
                if self._cr.rowcount:
                    pedidos_vinculados = self._cr.fetchall()
                    for ped_vin in pedidos_vinculados:
                        if ped_vin[0] not in ship.mapped('line_ids').mapped('sale_order_id').mapped('id'):
                            raise UserError(
                                _('You need to add the Order %s, due is Linked to another order present in this shipment') % (ped_vin[1]))
        return res

    @api.multi
    def prepare_shipment(self):
        return self.write({'state': 'confirm'})

    @api.multi
    def done(self):
        ship_line_obj = self.env['mrp.shipment.line']
        ship_sale_obj = self.env['mrp.shipment.sale']
        concat = ''
        concatenate = ''
        ordenes = []
        add = []
        for ship in self:
            concat += ship.folio + ';' + ship.reference + ';' +\
                str(ship.date) + ';' + str(ship.departure_date) + ';' +\
                str(ship.meters) + ';' + str(ship.freight) + ';' +\
                str(ship.amount)
            for line in ship.line_ids:
                sale_order_id = line.sale_order_id
                self._cr.execute("""SELECT so.name
                                    FROM pedidos_vinculados_sale_order_rel as pvs
                                    JOIN pedidos_vinculados_sale_order_rel as pvs2 on(pvs2.pedidos_vinculados_id = pvs.pedidos_vinculados_id)
                                    JOIN sale_order so ON so.id = pvs2.sale_order_id
                                    LEFT JOIN pedidos_vinculados as pv ON (pv.id = pvs.pedidos_vinculados_id)
                                    WHERE pv.activo = true AND pvs.sale_order_id = %s""", ([sale_order_id.id]))
                if self._cr.rowcount:
                    resultado = self._cr.fetchall()
                    for x in resultado:
                        for i in x:
                            if i not in add:
                                add.append(i)
                if line.quantity_shipped == 0:
                    line.unlink()
                    ship_line = ship_line_obj.search([
                        ('sale_order_id', '=', sale_order_id.id),
                        ('shipment_id', '=', ship.id)])
                    if not ship_line:
                        ship_sale = ship_sale_obj.search([
                            ('sale_id', '=', sale_order_id.id),
                            ('shipment_id', '=', ship.id)])
                        if ship_sale:
                            ship_sale.unlink()
                else:
                    volume = line.quantity_shipped * line.product_id.volume
                    weight = line.quantity_shipped * line.product_id.weight
                    if not line.city:
                        raise UserError(
                            _('The lines of order %s have no city.') % (
                                sale_order_id.name))
                    if not line.street:
                        raise UserError(
                            _('The lines of order %s have no street.') % (
                                sale_order_id.name))
                    if not line.state_id.name:
                        raise UserError(
                            _('The lines of order %s have no state.') % (
                                sale_order_id.name))
                    if not line.country_id.name:
                        raise UserError(
                            _('The lines of order %s have no country.') % (
                                sale_order_id.name))
                    if not line.partner_id.name:
                        raise UserError(
                            _('The lines of order %s have no partner.') % (
                                sale_order_id.name))
                    concatenate += line.partner_id.name + ';' +\
                        line.country_id.name + ';' + line.state_id.name +\
                        ';' + line.city + ';' + line.street + ' '
                    if line.street2:
                        concatenate += line.street2
                    concatenate += ';' + line.sale_order_id.name + ';' +\
                        line.sale_order_id.warehouse_id.name + ';' +\
                        line.sale_order_id.warehouse_id.code + ';' +\
                        str(line.sale_order_id.perc_freight) + ';' +\
                        line.product_code + ';' + line.product_name + ';' +\
                        str(volume) + ';' + str(weight) + ';' +\
                        str(line.quantity_shipped) + ';' +\
                        str(line.standard_cost) + ';' +\
                        str(line.price_unit) + '|'
                for a in ship.line_ids:
                    new = a.sale_order_id.name
                    if new not in ordenes:
                        ordenes.append(new)
            if add:
                for op in add:
                    if op not in ordenes:
                        raise UserError(
                            _('You need to add the Order %s, due is Linked to another order present in this shipment') % (op))
            ship.state = 'done'
        return concat, concatenate

    @api.multi
    def cancel(self):
        for ship in self:
            for line in ship.line_ids:
                line.quantity_shipped = 0
                line.order_line_id._quantity_shipped()
            ship.state = 'cancel'
        return True

    @api.multi
    def finished(self):
        shipment_line_obj = self.env['mrp.shipment.line']
        for ship in self:
            for line in ship.line_ids:
                sale_line = line.order_line_id
                shipment_line = shipment_line_obj.search(
                    [('order_line_id', '=', sale_line.id),
                     ('id', '!=', line.id)])
                qty_shipment = 0
                for ship_line in shipment_line:
                    qty_shipment += ship_line.quantity_shipped
                qty_invoiced = sale_line.qty_invoiced - qty_shipment
                if line.quantity_shipped > qty_invoiced:
                    if qty_invoiced < 0:
                        line.quantity_shipped = 0
                    else:
                        line.quantity_shipped = qty_invoiced
            ship.state = 'finished'
        return True

    @api.multi
    def add(self):
        return {
            'name': 'Add Sale Order',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.shipment.sale.order',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': self._context,
        }

    def _get_invoices(self):
        invoices = []
        for line in self.line_ids:
            inv_line_ids = line.order_line_id.invoice_lines
            invoice = self.env['account.invoice'].search([
                ('id', 'in', inv_line_ids.mapped('invoice_id').ids),
                ('state', '!=', ['cancel', 'draft']),
                ('type', '=', 'out_invoice')], order='id desc', limit=1)
            if invoice and invoice not in invoices:
                invoices.append(invoice)
        return ''.join(inv.number + ', ' for inv in invoices)[:-2]

class MrpShipmentSale(models.Model):
    _name = 'mrp.shipment.sale'
    _description = 'descripcion pendiente'

    sale_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
    )
    shipment_id = fields.Many2one(
        'mrp.shipment',
        string='Shipment',
        ondelete='cascade',
        index=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )
    partner_shipping_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )
    country_id = fields.Many2one(
        'res.country',
        string='Country',
    )
    state_id = fields.Many2one(
        'res.country.state',
        string='State',
    )
    city = fields.Char(
        string='City',
    )
    line_ids = fields.One2many(
        'mrp.shipment.line',
        'shipment_sale_id',
        string='Shipment Line',
        readonly=False,
        copy=True
    )

    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Line',
    )
    volume = fields.Float(
        string='Volume',
        compute='_compute_volume_shipped',
    )

    weight = fields.Float(
        string='Weight',
        compute='_compute_weight_shipped',
    )

    sequence = fields.Integer(
        string='Sequence',
    )

    # date = fields.Date(
    #     string='Date of shipment',
    #     related=shipment_id.date,
    #     readonly=True,
    # )

    # departure_date = fields.Date(
    #     string='Departure date',
    #     related=shipment_id.departure_date,
    #     readonly=True,
    # )

    def _compute_volume_shipped(self):
        volum = 0.0
        for line in self:
            for order in line.sale_id:
                self._cr.execute("""SELECT sum(pp.volume * msl.quantity_shipped)
                                    FROM mrp_shipment_line as msl
                                    JOIN sale_order as so ON so.id = msl.sale_order_id
                                    JOIN product_product as pp ON (pp.id = msl.product_id)
                                    WHERE msl.shipment_sale_id =  %s""", ([line.id]))
                if self._cr.rowcount:
                    volum = self._cr.fetchone()[0]
            line.volume = volum

    # @api.depends('sale_line_id')
    def _compute_weight_shipped(self):
        weigh = 0
        for linee in self:
            for order in linee.sale_id:
                self._cr.execute("""SELECT sum(pp.weight * msl.quantity_shipped)
                                    FROM mrp_shipment_line as msl
                                    JOIN sale_order as so ON so.id = msl.sale_order_id
                                    JOIN product_product as pp ON (pp.id = msl.product_id)
                                    WHERE msl.shipment_sale_id =  %s""", ([linee.id]))
                if self._cr.rowcount:
                    weigh = self._cr.fetchone()[0]
            linee.weight = weigh

    @api.multi
    def unlink(self):
        for sale in self:
            for line in sale.line_ids:
                if line.quantity_shipped != 0:
                    raise ValidationError(_("The quantity shipped in a \
                        line is different from 0"))
        return super(MrpShipmentSale, self).unlink()


class MrpShipmentLine(models.Model):
    _name = 'mrp.shipment.line'
    _description = 'Shipment line'

    shipment_id = fields.Many2one(
        'mrp.shipment',
        string='Shipment',
        ondelete='cascade',
        index=True
    )
    shipment_sale_id = fields.Many2one(
        'mrp.shipment.sale',
        string='Shipment Sale',
        ondelete='cascade',
        index=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )
    partner_shipping_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )
    country_id = fields.Many2one(
        'res.country',
        string='Country',
    )
    state_id = fields.Many2one(
        'res.country.state',
        string='State',
    )
    city = fields.Char(
        string='City',
    )
    street = fields.Char(
        string='Street',
    )
    street2 = fields.Char(
        string='Street2',
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale order',
    )
    order_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale order line ',
    )
    quantity = fields.Float(
        string='Quantity',
    )
    quantity_shipped = fields.Float(
        string='Quantity shipped',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    product_name = fields.Char(
        string='Name product',
    )
    product_code = fields.Char(
        string='Code product',
    )
    standard_cost = fields.Float(
        string='Standard cost',
    )
    price_unit = fields.Float(
        string='Price Unit',
    )
    total_price = fields.Float(
        string='Total price',
        compute='_compute_total_price'
    )
    total_cost = fields.Float(
        string='Total cost',
        compute='_compute_total_cost'
    )

    # date = fields.Date(
    #     string='Date of shipment',
    #     related=shipment_id.date,
    #     readonly=True,
    # )

    # departure_date = fields.Date(
    #     string='Departure date',
    #     related=shipment_id.departure_date,
    #     readonly=True,
    # )

    @api.depends('price_unit', 'quantity_shipped')
    def _compute_total_price(self):
        for line in self:
            line.total_price = line.price_unit * line.quantity_shipped

    @api.depends('standard_cost', 'quantity_shipped')
    def _compute_total_cost(self):
        for line in self:
            line.total_cost = line.standard_cost * line.quantity_shipped

    @api.constrains('quantity_shipped')
    def _check_quantity_shipped(self):
        for line in self:
            if line.quantity_shipped > line.quantity:
                raise ValidationError(_("The quantity available is less than \
                                      the quantity shipped"))

    @api.multi
    def unlink(self):
        for line in self:
            if line.quantity_shipped != 0:
                raise ValidationError(_("The quantity shipped in a \
                    line is different from 0"))
        return super(MrpShipmentLine, self).unlink()


class MrpShipmentPartner(models.Model):
    _name = 'mrp.shipment.partner'
    _description = 'Shipment partner'
    _order = 'sequence asc'

    shipment_id = fields.Many2one(
        'mrp.shipment',
        string='Shipment',
        index=True
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )

    sequence = fields.Integer(
        string='Sequence',
    )

    date_arrival = fields.Date(
        string='Time arrival date',
        store=True,
    )

    maniobras = fields.Boolean(
        string='Maniobras',
        store=True,
    )

    @api.model
    def delete_partner_not_shipment_id(self):
        partners = self.search([('shipment_id', '=', False)])
        for partner in partners:
            partner.unlink()
