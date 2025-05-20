# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class TmsTravelTollstation(models.Model):
    _name = 'tms.travel.tollstation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "date desc"

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        required=True
    )
    name = fields.Char(
        string='Tollstation name'
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('authorized', 'Waiting for authorization'),
         ('approved', 'Approved'),
         ('confirmed', 'Confirmed'),
         ('closed', 'Closed'),
         ('cancel', 'Cancelled'), ],
        readonly=True,
        default='draft'
    )
    date = fields.Date(
        required=True,
        default=fields.Date.context_today
    )
    travel_id = fields.Many2one(
        'tms.travel',
        string='Travel'
    )
    unit_id = fields.Many2one(
        'fleet.vehicle',
        compute='_compute_unit_id',
        string='Unit',
        store=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        compute='_compute_employee_id',
        string='Driver',
        store=True,
    )
    amount = fields.Monetary(
        required=True
    )
    notes = fields.Text()
    move_id = fields.Many2one(
        'account.move', 'Journal Entry',
        help="Link to the automatically generated Journal Items.\nThis move "
        "is only for Travel Expense Records with balance < 0.0",
        readonly=True
    )
    paid = fields.Boolean(
        compute='_compute_paid',
        readonly=True,
        store=True,
    )
    payment_move_id = fields.Many2one(
        'account.move',
        string="Payment Entry",
        readonly=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        'Currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id
    )
    expense_id = fields.Many2one(
        'tms.expense',
        'Expense Record',
        readonly=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        domain=[('tms_product_category', '=', 'tollstations')]
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        'Invoice',
        readonly=True,
        domain=[('state', '!=', 'cancel')],
    )
    invoice_paid = fields.Boolean(
        compute='_compute_invoiced_paid'
    )

    operador = fields.Char(
        string='Operador',
    )

    red = fields.Char(
        string='Red',
    )

    tag = fields.Char(
        string='Tag',
    )

    num_economico = fields.Char(
        string='N° Economico',
    )

    category = fields.Char(
        string='Categoria',
    )

    fecha_cruze = fields.Datetime(
        string='Fecha de Cruze',
    )

    num_plaza = fields.Char(
        string='N° Plaza',
    )

    nombre_plaza = fields.Char(
        string='Nombre Plaza',
    )

    tramo = fields.Char(
        string='Tramo',
    )

    carril = fields.Char(
        string='Carril',
    )

    importe_total = fields.Float(
        string='Importe al 100%',
    )

    importe_descuento = fields.Float(
        string='Importe (Con Desc.)',
    )

    dictaminacion = fields.Char(
        string='Dictaminacion',
    )

    id_pago = fields.Char(
        string='Id Pago',
    )

    @api.depends('invoice_id')
    def _compute_invoiced_paid(self):
        for rec in self:
            rec.invoice_paid = (
                rec.invoice_id.id and
                rec.invoice_id.state == 'paid')

    @api.multi
    @api.depends('travel_id')
    def _compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.travel_id.unit_id.id

    @api.depends('travel_id')
    def _compute_employee_id(self):
        for rec in self:
            rec.employee_id = rec.travel_id.employee_id.id

    @api.depends('payment_move_id')
    def _compute_paid(self):
        for rec in self:
            status = False
            if rec.payment_move_id:
                status = True
            rec.paid = status

    @api.onchange('travel_id')
    def _onchange_travel_id(self):
        self. unit_id = self.travel_id.unit_id.id
        self.employee_id = self.travel_id.employee_id.id

    @api.model
    def create(self, values):
        res = super().create(values)
        if res.amount <= 0:
            raise ValidationError(
                _('The amount must be greater than zero.'))
        return res

    @api.multi
    def action_authorized(self):
        for rec in self:
            rec.state = 'approved'

    @api.multi
    def action_approve(self):
        for rec in self:
            if rec.amount > rec.operating_unit_id.credit_limit:
                rec.state = "authorized"
            else:
                rec.state = 'approved'
                rec.message_post(_('<strong>Tollstation approved.</strong>'))

    @api.multi
    def action_cancel(self):
        for rec in self:
            if rec.invoice_id:
                raise ValidationError(
                    _('Could not cancel Fuel Voucher !'),
                    _('This Fuel Voucher is already Invoiced'))
            if (rec.travel_id and
               rec.travel_id.state == 'closed'):
                raise ValidationError(
                    _('Could not cancel Fuel Voucher !'
                        'This Fuel Voucher is already linked to Travel '
                        'Expenses record'))
            rec.state = 'cancel'

    @api.multi
    def action_cancel_draft(self):
        for rec in self:
            if rec.travel_id.state == 'cancel':
                raise ValidationError(
                    _('Could not set this tollstation to draft because'
                        ' the travel is cancelled.'))
            rec.state = 'draft'
            rec.message_post(_('<strong>Tollstation drafted.</strong>'))

    @api.multi
    def action_confirm(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(
                    _('Liters, Taxes and Total'
                      ' must be greater than zero.'))
            rec.message_post(body=_('<b>Fuel Voucher Confirmed.</b>'))
            rec.state = 'confirmed'
