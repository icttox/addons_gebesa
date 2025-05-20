# -*- coding: utf-8 -*-
# © 2023 Samuel Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import ValidationError


class MrpProductionSegment(models.TransientModel):
    _inherit = 'mrp.production.segment'

    def data_validate(self, production):
        if self.location_id != production.procurement_location_id:
            raise ValidationError(_(
                "The production order %s does not belong to the selected location") % (
                    production.name))
