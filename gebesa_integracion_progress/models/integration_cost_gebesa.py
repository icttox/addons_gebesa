# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class IntegrationCostGebesa(models.Model):
    _inherit = 'integration.cost.gebesa'

    @api.multi
    def integrates_costs(self):
        res = super().integrates_costs()
        concat = ''
        for line in res:
            concat += str(line[0].picking_id.numctrl_progress) \
                + ";" + str(line[1]) + " " \
                + str(line[2]) + ";" \
                + str(line[3]) + ";" \
                + str(line[4]) \
                + ";" + str(line[5]) + "|"
        self[0].concat_progress = concat
