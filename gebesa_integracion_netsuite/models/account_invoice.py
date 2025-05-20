# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import traceback
import logging
from odoo import api, models
from odoo import tools
from suds.client import Client

_logger = logging.getLogger()


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_move_create(self):
        res = super().action_move_create()

        for inv in self:
            if inv.type != 'out_invoice':
                continue

            if not inv.sale_id.id:
                continue

            TranID = inv.sale_id._name

            ped_extid = self.env['ir.model.data'].search(
                                [('module', '=', 'pedido'),
                                 ('model', '=', 'sale_order'),
                                 ('res_id', '=', inv.sale_id.id)],
                limit=1) or False

            if not ped_extid:
                continue

            SO_internalId = self.env['ir.model.data'].browse(
                self._cr, self._uid, ped_extid[0], context=self._context).name

            detalleSer = ''
            for line in inv.invoice_line:
                detalleSer += str(line.quantity) + ';' + str(
                    line.netsuite_line) + '|'

            return super().procesa_pedido_netsuite(
                self._cr, self._uid, self._ids, TranID, SO_internalId,
                detalleSer, context=self._context)

        return True


    def actualiza_ns(self, _cr, _uid, _ids, context=None):

        for inv in self:
            if inv.type != 'out_invoice':
                continue

            if not inv.sale_id.id:
                continue

            TranID = inv.sale_id.name

            ped_extid = self.env['ir.model.data'].search(self._cr, self._uid, [
                ('module', '=', 'pedido'),
                ('model', '=', 'sale.order'),
                ('res_id', '=', inv.sale_id.id)],
                limit=1, context=context) or False

            if not ped_extid:
                continue

            SO_internalId = self.env['ir.model.data'].browse(
                self._cr, self._uid, ped_extid[0], context=self._context).name

            detalleSer = ''
            for line in inv.invoice_line:
                detalleSer += str(line.quantity) + ';' + str(
                    line.netsuite_line) + '|'

            return super().procesa_pedido_netsuite(
                self._cr, self._uid, self._ids, TranID, SO_internalId,
                detalleSer, context=context)

        return True


    def procesa_pedido_netsuite(self, _cr, _uid, _ids, TranID, SO_internalId, detalleSer, context=None):
        try:
            if context is None:
                context = {}

            client = Client(
                'http://148.244.148.218:8089/FacturaNetSuite/\
                FacturaNetSuite.asmx?wsdl')

            resultado = client.service.doInvoice(
                SO_internalId, TranID, detalleSer)

            mensaje = tools.ustr(client.last_received())
            RespNetSuite = str(mensaje)

            self.write(self._cr, self._id, self._ids,
                       {'msj': RespNetSuite, 'netsuite_ok': True},
                       context=context)

            return True
        except Exception as e:
            error = tools.ustr(traceback.format_exc())
            error2 = str(e)
            self.write(self._cr, self._uid, self._ids, {'msj': error2},
                       context=context)
            _logger.error(error)
            return False
