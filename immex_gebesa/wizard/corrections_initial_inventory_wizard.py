# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models


class CorrectionsInitialInventoryWizard(models.TransientModel):
    _name = 'corrections.initial.inventory.wizard'
    _description = 'descripcion pendiente'

    report_replace = fields.Char(
        string='Informe a sustituir',
    )

    @api.multi
    def print_corrections_init_inventory(self):
        return self.env.ref(
            'immex_gebesa.immex_corrections_initial_inventory').report_action(
            self)
