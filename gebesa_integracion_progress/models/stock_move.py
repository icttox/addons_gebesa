# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import traceback
from odoo.exceptions import ValidationError
from odoo import api, models, tools
from suds.client import Client
from dateutil.parser import parse


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _action_done(self):
        """ Makes the move done and if all moves are done, it will finish the picking.
        @return:
        """
        res = super()._action_done()
        for move in self.browse():
            if move.stock_move_type_id.consecutive not in [
                    'E1', 'E2', 'S1', 'S2']:
                return res
        num_ctrl = 0
        folio_pro = ''
        num_ctrl, folio_pro = self.crea_movimiento_progress()
        for move in self.browse():
            move.numctrl_progress = num_ctrl
            move.folio_progress = folio_pro
            move.picking_id.numctrl_progress = num_ctrl
            move.picking_id.folio_progress = folio_pro
        return res

    def crea_movimiento_progress(self):
        """
        @params fdata : File.xml codification in base64
        """

        encabezado = ""
        detalle = ""

        encabezado = self.serializa_encabezado()
        detalle = self.serializa_detalle()

        wsdl_url = 'http://148.244.148.218:8060/wsa/wsa1/wsdl?target\
                    URI=urn:services-progress-com:cttox:wsainv001w'
        client = Client(wsdl_url, timeout=3600)

        conn = client.factory.create('S2:Connect_wsainv001w')
        conn.userId = 'supervisor'
        conn.password = 'gierp'

        uuid_prog = client.factory.create('S2:wsainv001wID')
        try:
            con_resp = client.service.Connect_wsainv001w(conn)
            token = client.last_received().getChild(
                "SOAP-ENV:Envelope").getChild("SOAP-ENV:Header").getChild(
                    "wsainv001wID").getChild("UUID").getText()
            uuid_prog.UUID = token
        except Exception as e:
            error = tools.ustr(traceback.format_exc())
            raise ValidationError("Ocurrio un error al firmarse en Progress favor de \
                    notificar al Administrador del sistema")
        parame = client.factory.create('S2:wsainv001w')
        parame.gcENCABEZADO = encabezado
        parame.gcDETALLE = detalle

        client.set_options(soapheaders=[uuid_prog])
        try:
            resuelto = client.service.wsainv001w(encabezado, detalle)

            mensaje = resuelto.gcRESPONSE.split('|')
            libera = client.service.Release_wsainv001w()

        except Exception as e:
            error = tools.ustr(traceback.format_exc())
            raise ValidationError('Ocurrio un error al enviar Movimiento a \
                                  Progress favor de notificar al \
                                  Administrador del sistema')

        if mensaje[0] == 'ERROR':
            raise ValidationError(mensaje[1])

        return mensaje[1], mensaje[2]

    def serializa_encabezado(self):
        """
        @params fdata : File.xml codification in base64
        """
        user_obj = self.env['res.users']

        picking_brw = self.browse(self.ids).picking_id
        usu_name = user_obj.browse(self._uid).name

        por_flete = 0.0
        if picking_brw.sale_id:
            por_flete = picking_brw.sale_id.flete_porc

        cve_tmd = picking_brw.stock_move_type_id.consecutive

        depto_id = 0
        origen = ''
        pedido = 0
        moneda_id = 1
        if cve_tmd in ['S1', 'S2']:
            depto_id = self.browse(self.ids).location_id.id
        elif cve_tmd in ['E1', 'E2']:
            depto_id = self.browse(self.ids).location_dest_id.id

        if picking_brw.sale_id:
            origen = 'Pedido de Venta: ' + picking_brw.sale_id.name
            pedido = picking_brw.sale_id.name
            moneda_id = picking_brw.sale_id.currency_id.id
        elif picking_brw.purchase_id:
            origen = 'Orden de Compra: ' + picking_brw.purchase_id.name
            moneda_id = picking_brw.purchase_id.currency_id.id
        else:
            if picking_brw.partner_id.customer:
                moneda_id = picking_brw.partner_id.\
                    property_product_pricelist.currency_id.id
            elif picking_brw.partner_id.supplier:
                moneda_id = picking_brw.partner_id.\
                    property_product_pricelist_purchase.currency_id.id

        depto_extid = self.env['ir.model.data'].search(
            [('module', '=', 'ubicacion'),
             ('model', '=', 'stock.location'),
             ('res_id', '=', depto_id)],
            limit=1)

        depto_numctrl = self.env['res.users'].browse(depto_extid[0]).name

        observaciones = 'Movimiento creado desde OpenERP por: ' + usu_name \
            + ', Partner: ' + picking_brw.partner_id.name \
            + ', Folio en OpenERP: ' + picking_brw.name + ', Origen: ' \
            + origen + ', Tipo: ' + picking_brw.dev_tipo

        # Dolares
        if moneda_id == 3:
            moneda_id = 2
        # Pesos
        elif moneda_id == 34:
            moneda_id = 1
        # Euros
        elif moneda_id == 1:
            moneda_id = 3

        fecha = parse(picking_brw.date).strftime('%d/%m/%Y')
        encabezado = picking_brw.name + ';' + str(picking_brw.id) + ';' \
            + str(picking_brw.partner_id.numctrl_progress) + ';' \
            + str(moneda_id) + ';' + str(por_flete) + ';' + fecha + ';' \
            + cve_tmd + ';' + str(depto_numctrl) + ';' + observaciones \
            + ';' + str(pedido)

        return encabezado

    def serializa_detalle(self):
        """
        @params fdata : File.xml codification in base64
        """
        detalle = ''
        for movimiento in self.browse():
            if movimiento.product_id.type != 'product':
                continue

            art_num_ctrl = movimiento.product_id.numctrl_progress or False

            if not art_num_ctrl:
                raise ValidationError('El producto %s no no esta ligada a \
                                      progress!'
                                      % movimiento.product_id.default_code)

            detalle += str(art_num_ctrl) + ',' + str(movimiento.product_qty) \
                + ',' + str(movimiento.precio_compra_venta) + ',|'
        return detalle
