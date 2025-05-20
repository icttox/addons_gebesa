from odoo import models, fields


class TmsPlace(models.Model):
    _name = 'tms.place'
    _inherit = 'tms.place'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )
