# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class MrpShipmentLine(models.Model):

    _inherit = 'mrp.shipment.line'

    packages_number = fields.Integer(string="Packages number", default=1)
