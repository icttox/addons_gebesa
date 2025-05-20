# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import traceback
from odoo import api, models, tools
from odoo.exceptions import ValidationError
from suds.client import Client


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def integracion(self):
        for picking in self.browse():
            for move in picking.move_line:
                if move.state == 'done' and \
                        move.stock_move_type_id.consecutive in [
                        'E1', 'E2', 'S1', 'S2']:
                    num_ctrl = 0
                    folio_pro = ''

                    numctrl_progress = move.numctrl_progress or False
                    folio_progress = move.folio_progress or False
                    if numctrl_progress or folio_progress:
                        return {}

                    num_ctrl, folio_pro = move.crea_movimiento_progress()
                    move.numctrl_progress = num_ctrl
                    move.folio_progress = folio_pro
                    move.picking_id.numctrl_progress = num_ctrl
                    move.picking_id.folio_progress = folio_progress
        return {}

    @api.multi
    def cancela_moviento_progress(self):
        msg = ''

        for picking in self.browse():
            wsdl_url = 'http://148.244.148.218:8060/wsa/wsa1/wsdl?targetURI=urn:\
                services-progress-com:cttox:wsainv002w'
            client = Client(wsdl_url, timeout=3600)

            conn = client.factory.create('S2:Connect_wsainv002w')
            conn.userId = 'supervisor'
            conn.password = 'gierp'

            uuid_prog = client.factory.create('S2:wsainv002wID')
            try:
                con_resp = client.service.Connect_wsainv002w(conn)
                token = client.last_received().getChild(
                    "SOAP-ENV:Envelope").getChild("SOAP-ENV:Header").getChild(
                        "wsainv002wID").getChild("UUID").getText()
                uuid_prog.UUID = token
            except Exception as e:
                error = tools.ustr(traceback.format_exc())
                raise ValidationError(
                    "Ocurrio un error al firmarse en Progress favor de \
                        notificar al Administrador del sistema")

            client.set_options(soapheaders=[uuid_prog])
            numctrl = str(picking.numctrl_progress)
            try:
                resuelto = client.service.wsainv002w(numctrl)
                mensaje = resuelto.mOUTPUTPAR.split('|')
                libera = client.service.Release_wsainv002w()

            except Exception as e:
                error = tools.ustr(traceback.format_exc())
                raise ValidationError(
                    "Ocurrio un error al enviar Movimiento a Progress favor \
                        de notificar al Administrador del sistema")

            if mensaje[0] == 'ERROR':
                raise ValidationError(mensaje[1])

        return {'message': msg}
