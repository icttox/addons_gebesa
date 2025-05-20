# Copyright 2023, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class ReadPayrollMicrosip(models.TransientModel):
    _name = 'read.payroll.microsip'
    _description = 'Download payroll report from Microsip'

    date_start = fields.Date(
        string='Date start'
    )
    date_end = fields.Date(
        string='Date end'
    )

    def read_prepayroll_microsip(self):
        return self.env.ref(
            'gebesa_integracion_microsip.read_payroll_microsip_xlsx').report_action(self)
