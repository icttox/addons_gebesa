# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    send_provider_alert = fields.Boolean(
        string='Enviar alerta provedor',
        default=False
    )
