# -*- coding: utf-8 -*-

from odoo import models, fields


class HrConsultationPrescription(models.Model):
    _name = "hr.consultation.prescription"
    _inherit = ['message.post.show.all']
    _description = "Consultation Prescription"

    consultation_id = fields.Many2one(
        'hr.consultation',
        string="Consultation",
    )

    name = fields.Char(
        string='Name',
        required=True,
    )

    dose = fields.Char(
        string='Dose',
        required=True,
    )
