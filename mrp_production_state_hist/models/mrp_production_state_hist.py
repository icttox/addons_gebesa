# -*- coding: utf-8 -*-

from odoo import models, fields


class MrpProductionStateHist(models.Model):

    _name = 'mrp.production.state.hist'

    production_id = fields.Many2one('mrp.production',
                                  string='Mrp production')
    date = fields.Date(string='Date')
    status_old = fields.Char(string='Last Status')
    status_new = fields.Char(string='New Status')
