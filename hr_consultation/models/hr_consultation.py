# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrConsultation(models.Model):
    _name = "hr.consultation"
    _inherit = ['message.post.show.all']
    _description = "Consultation"
    _order = 'name asc'
    _rec_name = 'name'

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        required=True,
    )

    nurse_id = fields.Many2one(
        'hr.employee',
        string="Nurse",
        required=True,
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company"
    )

    name = fields.Char(
        string='Name',
        size=250,
        required=True,
        index=True,
        copy=False,
        default='New',
        track_visibility='always')

    date = fields.Datetime(
        string='Date',
        required=True
    )

    diagnosis = fields.Html(
        string='Diagnosis',
    )

    symptoms = fields.Html(
        string='Symptoms',
    )

    medications_ids = fields.One2many(
        'hr.consultation.prescription',
        'consultation_id',
        string="Consultation Prescription"
    )

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
         'This field must be unique!')
    ]

    @api.model
    def create(self, vals_list):
        if vals_list.get('name', 'New') == 'New':
            vals_list['name'] = self.env['ir.sequence'].next_by_code(
                'hr.consultation') or '/'
        return super().create(vals_list)
