# Copyright 2023, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError
from odoo import fields, models, api


class DispersionDiesel(models.Model):
    _name = 'dispersion.diesel'
    _inherit = ['message.post.show.all']
    _rec_name = 'folio'
    _description = 'Dispersion diesel'
    _order = 'create_date desc'

    folio = fields.Char(
        string='Folio',
    )

    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done'),
         ('cancel', 'Cancelled')],
        readonly=True,
        default='draft'
    )

    folio_fisico = fields.Integer(
        string='Folio fisico',
        required=True,
        default=False,
    )

    date = fields.Datetime(
        string='Date',
        required=True,
        default=fields.Datetime.now,
    )

    ticket_number = fields.Char(
        string='Ticket number'
    )

    category = fields.Selection(
        [('local', 'Local'),
         ('foreigner', 'Foreigner'),
         ('third', 'Third')],
        string='Category',
        required=True
    )
    unit_id = fields.Many2one(
        'fleet.vehicle',
        string='Unidad',
        required=True,
    )

    cordinator_id = fields.Many2one(
        'hr.employee',
        string='cordinator',
        required=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        'Driver',
        domain=[('driver', '=', True)]
    )

    liters_qty = fields.Float(
        string='Liters',
        required=True,
        default=1.0
    )

    route_traveled = fields.Text(
        string='Route traveled'
    )

    km_traveled = fields.Float(
        string='Km traveled'
    )

    observations = fields.Text(
        string='Observations'
    )

    km_calculated = fields.Float(
        string='Km calculated',
        compute='_compute_calculated',
        store=True
    )

    liters_urea = fields.Float(
        string='Liters urea'
    )

    final_counter = fields.Integer(
        string='Final counter',
        required=True,
        default=False,
    )

    initial_counter = fields.Integer(
        string='Initial counter',
        required=True,
        default=False,
    )

    liters_calculated = fields.Float(
        string='Liters calculated',
        compute='_compute_liters_calculated'
    )

    counter_calculated = fields.Float(
        string='Counter calculated',
        compute='_compute_calculated',
        store=True
    )

    travel_ids = fields.One2many(
        'dispersion.diesel.travel',
        'dispersion_travel_id',
        string='Travel',
    )

    log_fuel_ids = fields.One2many(
        'fleet.vehicle.log.fuel',
        'dispersion_id',
        string='Log fuel',
    )

    # causa_folio_fisico = fields.Text(
    #     string='Motivo folio',
    # )

    causa_cotador_inicial = fields.Text(
        string='Motivo contador',
    )

    motivo = fields.Text(
        string='Motivo',
    )

    last_fill_date = fields.Date(
        string='Fecha del ultimo relleno',
        compute='_compute_last_fill_date',
        store=True
    )

    @api.multi
    @api.depends('unit_id')
    def _compute_last_fill_date(self):
        for record in self:
            date_last_fuel_log = self.env['fleet.vehicle.log.fuel'].search([
                ('vehicle_id', '=', record.unit_id.id)],
                order='date desc', limit=1)
            if date_last_fuel_log:
                record.last_fill_date = date_last_fuel_log.date
            else:
                record.last_fill_date = False

    @api.multi
    @api.depends('final_counter', 'initial_counter')
    def _compute_liters_calculated(self):
        for rec in self:
            rec.liters_calculated = rec.final_counter - rec.initial_counter

    @api.multi
    @api.depends('state', 'final_counter', 'km_traveled')
    def _compute_calculated(self):
        for record in self:
            last_record = self.search([
                ('create_date', '<', record.create_date),
                ('state', 'in', ['draft', 'done'])],
                order='create_date desc', limit=1)
            if last_record:
                record.counter_calculated = last_record.final_counter
                record.km_calculated = last_record.km_traveled
            else:
                record.counter_calculated = 0.0
                record.km_calculated = 0.0

    @api.constrains('folio_fisico')
    def _check_unique_folio_fisico(self):
        for record in self:
            existing_record = self.search([
                ('folio_fisico', '=', record.folio_fisico),
                ('id', '!=', record.id)
            ], limit=1)
            if existing_record:
                raise ValidationError("El folio físico ya existe en el sistema")

    @api.model
    def create(self, vals_list):
        # Se hace la busqueda del folio

        # existing_record = self.search([('folio_fisico', '=', vals_list['folio_fisico'] - 1)], limit=1)

        # Se hace la validacion si el folio es igual al mismo - 1
        # if not existing_record and not vals_list['causa_folio_fisico']:
        #     raise ValidationError("El campo 'Motivo folio' es obligatorio cuando el folio fisico anterior no esta en el sistema")

        vals_list['folio'] = self.env['ir.sequence'].next_by_code(
            'dispersion.diesel') or '/'
        return super().create(vals_list)

    @api.multi
    def action_validate(self):

        if self.initial_counter > self.final_counter:
            raise ValidationError("El contador inicial no puede ser mayor al contador final")

        if self.initial_counter != self.counter_calculated and not self.causa_cotador_inicial:
            raise ValidationError("El campo 'Motivo contador' es obligatorio cuando el contador inicial no es igual al contador final del registro anteriro")

        # Se busca el id del producto
        product = self.env['product.product'].search([
            ('type', '=', 'product'),
            ('tms_product_category', '=', 'fuel')],
            limit=1)

        log_fuel = self.env['fleet.vehicle.log.fuel']
        # Verificar si la suma de litros no coincide con el campo principal
        if self.category != 'foreigner':
            total_liters = sum(self.travel_ids.mapped('liters'))
            if total_liters != self.liters_qty:
                raise ValidationError('La suma de los litros en los viajes no coincide con los litros.')

            # Crear un vale de diesel por cada línea en la tabla de diesel por viajes
            for travel in self.travel_ids:
                if travel.tms_travel_id.unit_id != self.unit_id and not self.motivo:
                    raise ValidationError("El viaje %s, no pertenece a la unidad %s, por favor, proporciona el motivo." % (travel.tms_travel_id.name, self.unit_id.idname))
                new_log_fuel = log_fuel.create({
                    'operating_unit_id': self.env.user.default_operating_unit_id.id,
                    'vendor_id': self.env.user.company_id.partner_id.id,
                    'travel_id': travel.tms_travel_id.id,
                    'vehicle_id': travel.tms_travel_id.unit_id.id,
                    'product_qty': travel.liters,
                    'product_id': product.id,
                    'odometer': travel.tms_travel_id.unit_id.odometer,
                    'employee_id': travel.tms_travel_id.employee_id.id,
                    'ticket_number': self.ticket_number,
                    'dispersion_id': self.id,
                    'price_total': 0.00,
                    'tax_amount': 0.00,
                    'notes': self.observations,
                })
                # Se manda llamar el onchage de fuel log
                new_log_fuel._onchange_product_id()
                # Se manda llamar el metodo de aprovacion de fuel log
                new_log_fuel.action_approved()
                # Se manda llamar el metodo de cofirmacion de fuel log
                new_log_fuel.action_confirm()
        else:
            new_log_fuel = log_fuel.create({
                'operating_unit_id': self.env.user.default_operating_unit_id.id,
                'vendor_id': self.env.user.company_id.partner_id.id,
                # 'travel_id': travel.tms_travel_id.id,
                'vehicle_id': self.unit_id.id,
                'product_qty': self.liters_qty,
                'product_id': product.id,
                'odometer': self.unit_id.odometer,
                'employee_id': self.employee_id.id,
                'ticket_number': self.ticket_number,
                'dispersion_id': self.id,
                'price_total': 0.00,
                'tax_amount': 0.00,
                'notes': self.observations,
            })
            # Se manda llamar el onchage de fuel log
            new_log_fuel._onchange_product_id()
            # Se manda llamar el metodo de aprovacion de fuel log
            new_log_fuel.action_approved()
            # Se manda llamar el metodo de cofirmacion de fuel log
            new_log_fuel.action_confirm()

        # Actualizar el estado a "done" en la dispersion
        self.state = 'done'
        return True

    @api.multi
    def action_cancel(self):
        # Se cambia el estado a cancel en la dispersion
        for fuel_log in self.log_fuel_ids:
            fuel_log.with_context(cancel_from_dispersion=True).action_cancel()
        self.state = 'cancel'
        return True

    @api.multi
    def disperse_liters(self):
        for disp in self:
            total_km = sum(disp.travel_ids.mapped('tms_travel_id').mapped('distance_route'))
            total_liters = disp.liters_qty
            for line in disp.travel_ids:
                line_km = line.tms_travel_id.distance_route
                percent = round(line_km / total_km, 4)
                liters = round(disp.liters_qty * percent, 2)
                if total_liters < liters:
                    liters = total_liters

                line.liters = liters
                total_liters = total_liters - liters


class DispersionDieselTravel(models.Model):
    _name = 'dispersion.diesel.travel'
    _inherit = ['message.post.show.all']
    _description = 'descripcion pendiente'

    tms_travel_id = fields.Many2one(
        'tms.travel',
        string='Travel'
    )

    distance_route = fields.Float(
        related="tms_travel_id.distance_route"
    )

    liters = fields.Float(
        string='Liters'
    )

    dispersion_travel_id = fields.Many2one(
        'dispersion.diesel',
        string='Dispersion travel',
    )
    # unit_id = fields.Many2one(
    #     related='dispersion_travel_id.unit_id',
    #     string="Unit",
    # )

    _sql_constraints = [
        ('dispersion_travel_uniq', 'unique(dispersion_travel_id,tms_travel_id)',
         'A travel is doubled in dispersion!')
    ]
