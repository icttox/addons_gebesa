# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ReportQualityAlertWizard(models.Model):
    _name = 'report.quality.alert.wizard'
    _description = 'parameters to generate quality alert report'
