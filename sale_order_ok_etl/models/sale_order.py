# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import traceback
import logging
from odoo import _, api, models
from odoo import tools

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def force_validate(self):

        pending = self.env['sale.order'].search(
            [('state', 'in', ['draft', 'sent']),
             ('approve', '=', 'approved')], limit=25, order='date_approved')

        for order in pending:
            # dife = order.amount_total - order.total_nste
            # if abs(dife) > 0.6000:
            #     continue
            if not order.company_id.is_manufacturer:
                continue
            try:
                _logger.error(
                    _('Comienza validacion del pedido: %s' % order.name))
                order.action_confirm()
                self.env.cr.commit()
                _logger.error(
                    _('Termina validacion del pedido: %s' % order.name))
            except Exception:
                error = tools.ustr(traceback.format_exc())
                _logger.error(
                    _('Error al validar el pedido: %s' % order.name))
                _logger.error(
                    _('Error es: %s' % error))
                continue

            # except Exception:
            #     _logger.error(
            #         _('Error al validar el pedido %s' % order.name))
            #     continue
        return True
