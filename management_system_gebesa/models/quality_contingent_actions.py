# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class QualityContingentActions(models.Model):
    _name = 'quality.contingent.actions'
    _inherit = ['message.post.show.all']
    _description = 'descripcion pendiente'

    description = fields.Text(
        string='Description',
        required=True,
    )

    responsible_id = fields.Many2one(
        'hr.employee',
        string='Responsible',
        required=True,
    )

    date_commitment = fields.Date(
        string='Date commitment'
    )

    date_close = fields.Date(
        string='Date close'
    )

    corrective_action_id = fields.Many2one(
        'quality.corrective.action',
        string='Actions contingen',
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
        readonly=True,
    )
