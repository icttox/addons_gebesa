# -*- coding: utf-8 -*-
# © <2016> <Cesar Barron>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import api, models

_logger = logging.getLogger(__name__)


class MrpSegment(models.Model):
    _inherit = "mrp.segment"
    _name = "mrp.segment"
    _description = "cancel express"

    @api.model
    def cancel_express(self):
        segment_obj = self.env['mrp.segment']
        seg_var = segment_obj.search(
            [('state', '=', 'confirm'), ('express', '=', True)])
        if seg_var:
            for seg in seg_var:
                for line in seg.line_ids:
                    if line.mrp_production_id.state == 'confirmed':
                        line.mrp_production_id.write(
                            {'cancellation_reason': "Inventario Express"})
                        line.mrp_production_id.action_cancel()
                    self.env.cr.commit()
                if seg.state == 'confirm':
                    self._cr.execute("""UPDATE mrp_segment SET state = 'cancel' WHERE state='confirm'
                    and id = %s""", ([seg.id]))
        return True
