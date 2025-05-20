# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError


class TmsTravel(models.Model):
    _inherit = 'tms.travel'

    international = fields.Boolean(
        string='International',
    )
    in_out = fields.Selection(
        [
            ('in', 'In'),
            ('out', 'Out')],
        string='In/Out',
    )
    via_in_out_id = fields.Many2one(
        'l10n.mx.wbl.transport',
        string='Via in out',
    )
    delivery_ids = fields.One2many(
        'tms.travel.delivery',
        'travel_id',
        string='Deliverys',
    )
    insurance_policy = fields.Char()
    insurance_supplier_id = fields.Many2one(
        'res.partner', string='Insurance Supplier')
    environmental_insurance_policy = fields.Char()
    environmental_insurance_supplier_id = fields.Many2one(
        'res.partner', string='Environmental Insurance Supplier')

    dangerous_material = fields.Boolean(
        string='Dangerous material',
        compute="_compute_dangerous_material"
    )
    conf_vehicle_id = fields.Many2one(
        'l10n.mx.wbl.autotransport.conf',
        string='Autotransport Configuration',
    )
    l10n_mx_edi_reverse_logistics = fields.Boolean(
        string='Logistica Inversa',
    )

    @api.onchange('unit_id')
    def _onchange_travel_unit_id(self):
        for rec in self:
            rec.conf_vehicle = rec.unit_id.conf_vehicle.id

    @api.depends('transportable_line_ids', 'transportable_line_ids.transportable_id')
    def _compute_dangerous_material(self):
        for travel in self:
            travel.dangerous_material = False
            if any(line.transportable_id.dangerous for line in travel.transportable_line_ids):
                travel.dangerous_material = True

    @api.multi
    def action_progress(self):
        for travel in self:
            if not travel.insurance_supplier_id:
                raise UserError('This travel need a insurance supplier')
            if not travel.insurance_policy:
                raise UserError('This travel need a insurance policy')
        return super().action_progress()
