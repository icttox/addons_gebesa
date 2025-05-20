# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpProductionDailyLoad(models.Model):
    _name = 'mrp.production.daily.load'
    _description = 'descripcion pendiente'
    _order = 'id desc'

    work_id = fields.Many2one(
        'mrp.workcenter',
        string='Work',
        required=True,
    )

    operation_id = fields.Many2one(
        'mrp.operation',
        string='Operation',
        required=True,
    )

    routing_line_id = fields.Many2one(
        'mrp.routing.workcenter',
        string='Operacion centro de trabajo',
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        # domain=lambda self: self._default_domain_segment()
    )

    date_start = fields.Datetime(
        string='Date Start',
        required=True,
        default=fields.Datetime.now(),
    )

    date = fields.Datetime(
        string='Date',
        required=True,
        default=fields.Datetime.now(),
    )

    quantity = fields.Integer(
        string="Quantity",
        required=True,
    )

    name = fields.Char(
        string='Name',
        compute='_compute_load_name')

    costo = fields.Float(
        string='Costo',
        related='product_id.standard_price',
        readonly=True,
    )

    daily_observations = fields.Text(
        string='Daily Observations',
    )

    segment_id = fields.Many2one(
        'mrp.segment',
        string='Segmento',
    )

    planned_qty = fields.Float(
        string='Planned quantity',
        compute='_compute_planned_qty',
        default=0.00
    )

    active = fields.Boolean(
        string='Active',
        default=True,
    )

    costo_total = fields.Float(
        string='Costo total',
        store=True,
        compute='_compute_total',
        default=0.00
    )

    _sql_constraints = [
        (
            'key_uniq',
            'unique (date, work_id, operation_id, product_id, segment_id, routing_line_id)',
            'The combination of date, work center, operation, product and segment already exists.'),
    ]

    @api.depends('quantity', 'costo')
    def _compute_total(self):
        for cal in self:
            cal.costo_total = 0
            cal.costo_total = cal.quantity * cal.costo

    @api.onchange('segment_id')
    def _onchange_segment(self):
        dom = []
        if self.segment_id:
            dom = [("id", "in", self.segment_id.mapped('line_ids').mapped('product_id').ids)]
        self.product_id = False
        return {'domain': {'product_id': dom}}

    @api.depends('segment_id', 'product_id')
    def _compute_planned_qty(self):
        for record in self.filtered(lambda line: line.segment_id and line.product_id):
            totplanned = abs(sum(self.env['mrp.segment.line'].search(
                [
                    ('segment_id', '=', record.segment_id.id),
                    ('product_id', '=', record.product_id.id)
                ]).mapped('product_qty')))
            record.planned_qty = totplanned

    @api.model
    def create(self, vals_list):
        if vals_list.get('quantity') and vals_list.get('segment_id'):
            qty_registered = abs(sum(self.env['mrp.production.daily.load'].search(
                [
                    ('segment_id', '=', vals_list.get('segment_id')),
                    ('product_id', '=', vals_list.get('product_id')),
                    ('work_id', '=', vals_list.get('work_id')),
                    ('operation_id', '=', vals_list.get('operation_id')),
                    ('routing_line_id', '=', vals_list.get('routing_line_id'))
                ]).mapped('quantity'))) or 0.00

            totplanned = abs(sum(self.env['mrp.segment.line'].search(
                [
                    ('segment_id', '=', vals_list.get('segment_id')),
                    ('product_id', '=', vals_list.get('product_id'))
                ]).mapped('product_qty'))) or 0.00

            if (qty_registered + vals_list.get('quantity')) > totplanned:
                segment = self.env['mrp.segment'].browse([vals_list.get('segment_id')])
                product = self.env['product.product'].browse([vals_list.get('product_id')])
                raise UserError(_("The quantity of the product %s in the segment %s: %s is less than \n"
                                  "the total quantity done %s") % (
                                product.default_code,
                                segment.folio,
                                totplanned,
                                (qty_registered + vals_list.get('quantity')),
                                ))
        return super().create(vals_list)

    @api.multi
    def write(self, vals_list):
        if not any([vals_list.get('quantity'), vals_list.get('segment_id'),
           vals_list.get('product_id'), vals_list.get('work_id'),
           vals_list.get('operation_id')]):

            return super().write(vals_list)

        if vals_list.get('quantity'):
            quantiity = vals_list.get('quantity')
        else:
            quantiity = self.quantity

        if vals_list.get('segment_id'):
            segment_id = vals_list.get('segment_id')
        else:
            segment_id = self.segment_id.id

        if vals_list.get('product_id'):
            product_id = vals_list.get('product_id')
        else:
            product_id = self.product_id.id

        if vals_list.get('work_id'):
            work_id = vals_list.get('work_id')
        else:
            work_id = self.work_id.id

        if vals_list.get('operation_id'):
            operation_id = vals_list.get('operation_id')
        else:
            operation_id = self.operation_id.id

        qty_registered = abs(sum(self.env['mrp.production.daily.load'].search(
            [
                ('segment_id', '=', segment_id),
                ('product_id', '=', product_id),
                ('work_id', '=', work_id),
                ('operation_id', '=', operation_id)
            ]).mapped('quantity')))

        totplanned = abs(sum(self.env['mrp.segment.line'].search(
            [
                ('segment_id', '=', segment_id),
                ('product_id', '=', product_id)
            ]).mapped('product_qty')))

        if (qty_registered + quantiity) > totplanned:
            segment = self.env['mrp.segment'].browse([segment_id])
            product = self.env['product.product'].browse([product_id])
            raise UserError(_("The quantity of the product %s in the segment %s: %s is less than \n"
                              "the total quantity done %s") % (
                            product.default_code,
                            segment.folio,
                            totplanned,
                            (qty_registered + quantiity),
                            ))
        return super().write(vals_list)

    @api.depends('work_id', 'operation_id', 'product_id', 'date', 'segment_id')
    def _compute_load_name(self):
        for record in self:
            # datetime.strptime(record.date, "%Y/%m/%d %H-%M-%S")
            name = ''
            name = str(record.date.date()) + '_' + str(record.work_id.code) + '_' + str(record.operation_id.code) + '_' + str(record.product_id.default_code) + '_' + str(record.segment_id.folio)
            record.name = name

            # local_tz = pytz.timezone(self._context['tz'])
            # datetime_with_tz = local_tz.localize(create_date, is_dst=None)
            # date = fields.Datetime.to_string(datetime_with_tz.astimezone(pytz.utc))
            # record.date.replace('/', '-')
            # record.name = record.date + '_' + record.work_id.code + '_' + record.operation_id.code + '_' + record.product_id.default_code
