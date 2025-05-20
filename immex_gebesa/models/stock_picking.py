# -*- coding: utf-8 -*-

import re
from odoo import _, api, models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    country_fiscal_code = fields.Char(
        string='Codigo fiscal',
        related='partner_id.country_id.fiscal_code',
        readonly=True,
    )
    code_move_type = fields.Char(
        string='Codigo tipo de movimiento', size=5,
        related='stock_move_type_id.code',
        readonly=True,
    )
    pediment_number = fields.Char(
        string='Numero de pedimento',
        copy=False,
    )
    patente_aduanal = fields.Char(
        string='Patente aduanal',
        copy=False,
    )
    entry_date = fields.Datetime(
        string='Fecha de entrada',
        copy=False,
    )
    clave_aduanal = fields.Char(
        string='Clave aduanal',
        copy=False,
    )
    cove = fields.Char(
        string='COVE',
    )

    @api.onchange('pediment_number')
    def _onchange_pediment_number(self):
        pattern = re.compile("([0-9]{7}$)")
        if self.pediment_number:
            if not pattern.match(self.pediment_number):
                self.pediment_number = ''
                warning_mess = {
                    'title': _('Validation Error'),
                    'message': _('Please enter valid Petiment number.')
                }
                return {'warning': warning_mess}
        return {}

    @api.onchange('patente_aduanal')
    def _onchange_patente_aduanal(self):
        pattern = re.compile("([0-9]{4}$)")
        if self.patente_aduanal:
            if not pattern.match(self.patente_aduanal):
                self.patente_aduanal = ''
                warning_mess = {
                    'title': _('Validation Error'),
                    'message': _('Please enter valid Customs Patent.')
                }
                return {'warning': warning_mess}
        return {}

    @api.onchange('clave_aduanal')
    def _onchange_clave_aduanal(self):
        pattern = re.compile("([0-9]{3}$)")
        if self.clave_aduanal:
            if not pattern.match(self.clave_aduanal):
                self.clave_aduanal = ''
                warning_mess = {
                    'title': _('Validation Error'),
                    'message': _('Please enter valid Customs code.')
                }
                return {'warning': warning_mess}
        return {}
