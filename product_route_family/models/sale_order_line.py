# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        route_obj = self.env['stock.location.route']
        res = super().product_id_change()
        for line in self:
            line.route_id = False
            if line.product_id:
                if line.product_id.type == 'service':
                    continue
                if line.product_id.available_sale is not True:
                    raise UserError(_('Este producto esta inhabilitado para '
                                      'captura de pedidos %s.') % line.product_id.default_code)
                if not line.product_id.family_id:
                    warning_mess = {
                        'title': _('Odoo Warning!'),
                        'message': _('Product %s has no family assigned') %
                                    (line.product_id.default_code)
                    }
                    return {'warning': warning_mess}
                route_id = route_obj.search([('family_ids', '=',
                                              line.product_id.family_id.id)])
                if len(route_id) < 1:
                    warning_mess = {
                        'title': _('Odoo Warning!'),
                        'message': _('Family %s has not assigned a production route') %
                                    (line.product_id.family_id.name)
                    }
                    return {'warning': warning_mess}

                if len(route_id) > 1:
                    warning_mess = {
                        'title': _('Odoo Warning!'),
                        'message': _('Family %s has more than one production route assigned') %
                                    (line.product_id.family_id.name)
                    }
                    return {'warning': warning_mess}
                line.route_id = route_id.id
        return res
