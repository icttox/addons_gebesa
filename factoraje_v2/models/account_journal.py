# -*- coding: utf-8 -*-
# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    factoring_percentage = fields.Integer(
        string='Factoraje %',
    )
