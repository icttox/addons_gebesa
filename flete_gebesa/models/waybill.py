# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _, api, exceptions
from odoo.exceptions import UserError


class TmsWaybill(models.Model):
    _name = 'tms.waybill'
    _inherit = ['message.post.show.all', 'tms.waybill']

    order_id = fields.Many2one(
        'sale.order',
        string=_('Orden de Venta'),
    )
    amount_untaxed = fields.Float(
        compute='_compute_amount_untaxed',
        string='SubTotal',
        store=True,
    )
    amount_tax = fields.Float(
        compute='_compute_amount_tax',
        string='Taxes',
        store=True,
    )
    amount_total = fields.Float(
        compute='_compute_amount_total',
        string='Total',
        store=True,
    )

    motivo_cancel = fields.Char(
        string='Motivo de Cancelacion',
    )
    date_cancell = fields.Date(
        string='Cancellation date'
    )

    evidencia = fields.Boolean(
        string='Evidencias',
        copy=False,
    )

    unit = fields.Char(
        string='Unit',
        compute="_compute_travel_data",
    )
    trailer1 = fields.Char(
        string='Trailer1',
        compute="_compute_travel_data",
    )
    dolly = fields.Char(
        string='Dolly',
        compute="_compute_travel_data",
    )
    trailer2 = fields.Char(
        string='Trailer2',
        compute="_compute_travel_data",
    )
    route = fields.Char(
        string='Route',
        compute="_compute_travel_data",
    )
    driver = fields.Char(
        string='Driver',
    )

    @api.depends('travel_ids')
    def _compute_travel_data(self):
        for waybill in self:
            unit = ''
            trailer1 = ''
            dolly = ''
            trailer2 = ''
            route = ''
            driver = ''
            for travel in waybill.travel_ids:
                if travel.state != 'cancel':
                    if travel.unit_id:
                        unit = travel.unit_id.name + ', '
                    if travel.trailer1_id:
                        trailer1 += travel.trailer1_id.name + ', '
                    if travel.dolly_id:
                        dolly += travel.dolly_id.name + ', '
                    if travel.trailer2_id:
                        trailer2 += travel.trailer2_id.name + ', '
                    if travel.route_id:
                        route += travel.route_id.name + ', '
                    if travel.employee_id:
                        driver += travel.employee_id.name
            waybill.unit = unit[:-2]
            waybill.trailer1 = trailer1[:-2]
            waybill.dolly = dolly[:-2]
            waybill.trailer2 = trailer2[:-2]
            waybill.route = route[:-2]
            waybill.driver = driver[:-2]

    @api.multi
    def write(self, values):
        for rec in self:
            old_total = rec.amount_total
            res = super().write(values)
            new_total = rec.amount_total
        return res

    @api.multi
    def action_cancel(self):
        for waybill in self:
            if not waybill.motivo_cancel:
                raise UserError(_('Debes capturar el motivo de cancelacion de esta Carta Porte'))
            if not self.env.user.has_group('flete_gebesa.group_cancel_waybill_gebesa'):
                raise UserError(_('Solo Gerencia puede cancelar esta Carta Porte'))
            waybill.date_cancell = fields.Datetime.now()
            return super().action_cancel()

    @api.multi
    def action_approve(self):
        for waybill in self:
            if not self.env.user.has_group('flete_gebesa.group_validate_waybill_gebesa'):
                raise UserError(_('Error!\nNo tienes permiso para validar esta carta porte.\n'
                                'Check with your System Administrator.'))
            return super().action_approve()

    @api.multi
    def action_confirm(self):
        for waybill in self:
            if not self.env.user.has_group('flete_gebesa.group_validate_waybill_gebesa'):
                raise UserError(_('Error!\nYNo tienes permiso para confirmar esta carta porte.\n'
                                'Check with your System Administrator.'))
            return super().action_confirm()

    @api.multi
    def action_cancel_draft(self):
        for waybill in self:
            if not self.env.user.has_group('flete_gebesa.group_cancel_waybill_gebesa'):
                raise UserError(_('Solo Gerencia puede revertir a borrador esta Carta Porte'))
            for travel in waybill.travel_ids:
                if travel.state == 'cancel':
                    raise exceptions.ValidationError(
                        _('Could not set to draft this Waybill !\n'
                          'Travel is Cancelled !!!'))
            waybill.message_post(
                body=_("<h5><strong>Cancel to Draft</strong></h5>"))
            waybill.state = 'draft'

    @api.multi
    @api.onchange('order_id')
    def put_order_lines(self):
        res = {}
        for order in self.order_id:
            for line in order.order_line:
                res[line.id] = {
                    'product_id': line.product_id.id,
                    'waybill_id': self.id,
                    'discount': line.discount,
                    'product_qty': line.product_uom_qty,
                    'unit_price': line.price_unit,
                    'tax_amount': line.price_tax,
                    'tax_ids': line.tax_id,
                    'price_subtotal': line.price_subtotal,
                    'name': line.name}
            order_lines = self.waybill_line_ids.browse([])
            for i in res.values():
                order_lines += order_lines.new(i)
            self.waybill_line_ids = order_lines
        return

    @api.multi
    def action_waybill_send(self):
        '''
        This function opens a window to compose an email, for the Waybill
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference(
                'flete_gebesa', 'email_template_waybill')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'tms.waybill',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
