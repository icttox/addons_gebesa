# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    total_folios = fields.Integer(
        help='Helper number, when you buy a fixed number of Folios to your'
        ' PAC this number will be used to inform you if you are close to'
        ' finish your Folios, this will be informed in the administrator'
        ' Wall.')

    pac_id = fields.Many2one(
        'res.pac', 'PAC',
        help='PAC used to send Electronic Documents to sign and cancel.')
