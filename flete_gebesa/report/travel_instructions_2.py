# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import UserError


class ParticularReport(models.AbstractModel):
    _name = 'report.flete_gebesa.report_travel_instructions_2'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'tms.travel'
        #report_obj = self.env['report']
        #report = report_obj._get_report_from_name('flete_gebesa.report_travel_instructions_2')
        travel_obj = self.env['tms.travel']
        user_obj = self.env['res.users']
        travel_var = travel_obj.browse(docids)
        # import pdb; pdb.set_trace()
        user_var = user_obj.browse(self._uid)
        nombre_usuario = False
        nombre_usuario = user_var.partner_id.name
        travel = {}
        travel_operator = {}
        datos_viaje = {}
        totales = {}
        concatena = []
        for doc in travel_var:
            if not doc.shipment_id:
                raise UserError(_('This travel has not shipment'))
            travel[doc.id] = {}
            travel_operator[doc.id] = {}
            datos_viaje[doc.id] = {}
            totales[doc.id] = {}
            ship = doc.shipment_id.folio
            if ship not in travel[doc.id].keys():
                travel[doc.id]['Shipment'] = []
                datos_viaje[doc.id][ship] = []
                travel_operator[doc.id][ship] = []
                totales[doc.id][ship] = []

            # ORDENAMIENTO POR CLIENTE
            if len(doc.shipment_id.sale_ids.ids) == 1:
                limpio = tuple(doc.shipment_id.sale_ids.ids)[-1]
                self._cr.execute("""SELECT mss.id FROM mrp_shipment_sale as mss
                                        JOIN res_partner as rp ON (rp.id = mss.partner_id)
                                        JOIN sale_order as so ON (so.id = mss.sale_id)
                                        JOIN res_partner as rp2 ON (so.partner_shipping_id = rp2.id)
                                        JOIN stock_warehouse as sw ON (sw.id = so.warehouse_id)
                                    WHERE mss.id IN ({0})
                                    ORDER BY rp2.name""".format(limpio))
                if self._cr.rowcount:
                    ordenamiento = self._cr.fetchall()
            else:
                self._cr.execute("""SELECT mss.id FROM mrp_shipment_sale as mss
                                    JOIN res_partner as rp ON (rp.id = mss.partner_id)
                                    JOIN sale_order as so ON (so.id = mss.sale_id)
                                    JOIN res_partner as rp2 ON (so.partner_shipping_id = rp2.id)
                                    JOIN stock_warehouse as sw ON (sw.id = so.warehouse_id)
                                WHERE mss.id IN {0}
                                ORDER BY rp2.name""".format(tuple(doc.shipment_id.sale_ids.ids)))
                if self._cr.rowcount:
                    ordenamiento = self._cr.fetchall()

            for sale in ordenamiento:  # doc.shipment_id.sale_ids:
                # CLIENTES
                self._cr.execute("""SELECT rp2.name, so.name, so.credit_note, so.total_freight,
                                           so.amount_total, sw.name
                                FROM mrp_shipment_sale as mss
                                    JOIN res_partner as rp ON (rp.id = mss.partner_id)
                                    JOIN sale_order as so ON (so.id = mss.sale_id)
                                    JOIN res_partner as rp2 ON (so.partner_shipping_id = rp2.id)
                                    JOIN stock_warehouse as sw ON (sw.id = so.warehouse_id)
                                WHERE mss.id = %s
                                ORDER BY rp2.name""", ([sale[0]]))
                ordenn = False
                resultado = False
                credit_note = False
                flete = False
                importe = False
                almacen = False
                if self._cr.rowcount:
                    res = self._cr.fetchone()
                    resultado = res[0]
                    ordenn = res[1]
                    credit_note = res[2]
                    flete = res[3]
                    importe = res[4]
                    almacen = res[5]

                # FACTURAS
                self._cr.execute("""SELECT  ai.number
                                FROM mrp_shipment_sale as mss
                                    JOIN sale_order as so ON (so.id = mss.sale_id)
                                    JOIN res_partner as rp2 ON (so.partner_shipping_id = rp2.id)
                                    JOIN account_invoice as ai ON (ai.sale_id = so.id AND ai.travel_id = %s)
                                WHERE mss.id = %s
                                ORDER BY rp2.name""", (doc.id, sale[0]))
                if self._cr.rowcount:
                    factura = self._cr.fetchone()[0]
                else:
                    factura = 'S/F'

                travel[doc.id]['Shipment'].append({'id': sale[0],
                                                   'usuario': resultado,
                                                   'orden': ordenn,
                                                   'credit_note': credit_note,
                                                   'factura': factura,
                                                   'almacen': almacen,
                                                   'importe': importe,
                                                   'flete': flete,
                                                   'entrega': doc.shipment_id.departure_date
                                                   })
            # TRAVEL OPERATOR CLIENTE
            self._cr.execute("""SELECT CONCAT(rp2.name, ' - ', rcc.name)
                                FROM mrp_shipment_sale as mss
                                    JOIN sale_order as so ON (so.id = mss.sale_id)
                                    JOIN res_partner as rp2 ON (so.partner_shipping_id = rp2.id)
                                    JOIN res_city as rcc ON (rcc.id = rp2.city_id)
                                WHERE mss.shipment_id = %s
                                GROUP BY rp2.name, rcc.name
                                ORDER BY rp2.name""", ([doc.shipment_id.id]))
            if self._cr.rowcount:
                resultado = self._cr.fetchall()
                for x in resultado:
                    for i in x:
                        if i not in concatena:
                            concatena.append(i)

            travel_operator[doc.id][ship].append({'id': sale[0],
                                                  'concatena': concatena,
                                                  })
            # DATOS DEL VIAJE PESO
            # VERIFICACION SI TIENE PESO
            # self._cr.execute("""SELECT string_agg(pp.default_code, ',')
            #                    FROM mrp_shipment_sale as mss
            #                        JOIN mrp_shipment_line as msl ON (msl.shipment_sale_id = mss.id)
            #                        JOIN product_product as pp ON (pp.id = msl.product_id)
            #                        JOIN sale_order as so ON (so.id = mss.sale_id)
            #                        JOIN stock_warehouse as sw ON (sw.id = so.warehouse_id)
            #                    WHERE mss.shipment_id = %s
            #                        AND pp.weight IS NULL""", ([doc.shipment_id.id]))
            #if self._cr.rowcount:
            #    sin_peso = self._cr.fetchone()[0]
            #    if sin_peso:
            #        raise UserError(_('Estos Productos no tienen Peso %s') % (sin_peso))
            # PESOOOOO
            self._cr.execute("""SELECT ROUND(CAST(SUM(pp.weight * msl.quantity_shipped) AS NUMERIC),2)
                                FROM mrp_shipment_sale as mss
                                    JOIN mrp_shipment_line as msl ON (msl.shipment_sale_id = mss.id)
                                    JOIN product_product as pp ON (pp.id = msl.product_id)
                                    JOIN sale_order as so ON (so.id = mss.sale_id)
                                    JOIN stock_warehouse as sw ON (sw.id = so.warehouse_id)
                                WHERE mss.shipment_id = %s
                                GROUP BY sw.id
                                ORDER BY sw.code""", ([doc.shipment_id.id]))
            weight = 0
            if self._cr.rowcount:
                weight = self._cr.fetchall()

            # DATOS DEL VIAJE PESO
            self._cr.execute("""SELECT ROUND(CAST(SUM(pp.volume * msl.quantity_shipped) AS NUMERIC),2)
                                FROM mrp_shipment_sale as mss
                                    JOIN mrp_shipment_line as msl ON (msl.shipment_sale_id = mss.id)
                                    JOIN product_product as pp ON (pp.id = msl.product_id)
                                    JOIN sale_order as so ON (so.id = mss.sale_id)
                                    JOIN stock_warehouse as sw ON (sw.id = so.warehouse_id)
                                WHERE mss.shipment_id = %s
                                GROUP BY sw.id
                                ORDER BY sw.code""", ([doc.shipment_id.id]))
            volume = 0
            if self._cr.rowcount:
                volume = self._cr.fetchall()
            # DATOS DEL VIAJE FLETE POR PEDIDO
            self._cr.execute("""SELECT SUM(((sol.freight_amount / sol.product_uom_qty) * msl.quantity_shipped)* so.rate_mex)
                                FROM mrp_shipment_sale as mss
                                    JOIN mrp_shipment_line as msl ON (msl.shipment_sale_id = mss.id)
                                    JOIN sale_order_line as sol ON (sol.id = msl.order_line_id)
                                    JOIN sale_order as so ON (so.id = sol.order_id)
                                    JOIN stock_warehouse as sw ON (sw.id = so.warehouse_id)
                                WHERE mss.shipment_id = %s
                                GROUP BY sw.id
                                ORDER BY sw.code""", ([doc.shipment_id.id]))
            flete_pedido = False
            if self._cr.rowcount:
                flete_pedido = self._cr.fetchall()
            # AlMACENES
            self._cr.execute("""SELECT sw.name
                                FROM stock_warehouse as sw
                                ORDER BY sw.code""")
            almac = False
            if self._cr.rowcount:
                almac = self._cr.fetchall()

            # DATOS DEL VIAJE VOLUNE
            # VERIFICACION SI TIENE VOLUMEN
            # self._cr.execute("""SELECT string_agg(pp.default_code, ',')
            #                    FROM mrp_shipment_sale as mss
            #                        JOIN mrp_shipment_line as msl ON (msl.shipment_sale_id = mss.id)
            #                        JOIN product_product as pp ON (pp.id = msl.product_id)
            #                        JOIN sale_order as so ON (so.id = mss.sale_id)
            #                        JOIN stock_warehouse as sw ON (sw.id = so.warehouse_id)
            #                    WHERE mss.shipment_id = %s
            #                        AND pp.volume IS NULL""", ([doc.shipment_id.id]))
            # if self._cr.rowcount:
            #    sin_volumen = self._cr.fetchone()[0]
            #    if sin_volumen:
            #        raise UserError(_('Estos Productos no tienen Volumen %s') % (sin_volumen))
            # SUMATORIA DEL VOLUMEN
            self._cr.execute("""SELECT SUM(pp.volume * msl.quantity_shipped)
                                FROM mrp_shipment_sale as mss
                                    JOIN mrp_shipment_line as msl ON (msl.shipment_sale_id = mss.id)
                                    JOIN product_product as pp ON (pp.id = msl.product_id)
                                    JOIN sale_order as so ON (so.id = mss.sale_id)
                                    JOIN stock_warehouse as sw ON (sw.id = so.warehouse_id)
                                WHERE mss.shipment_id = %s """, ([doc.shipment_id.id]))
            tot = 0
            if self._cr.rowcount:
                tot = self._cr.fetchall()

            datos_viaje[doc.id][ship].append({'id': sale[0],
                                              'peso': weight,
                                              'volume': volume,
                                              'flete_pedido': flete_pedido,
                                              'almacen': almac,
                                              'tot': tot,
                                              })
            # SUMATORIAS
            self._cr.execute("""SELECT ROUND(CAST(SUM(pp.weight * msl.quantity_shipped)AS NUMERIC),2)
                                FROM mrp_shipment_sale as mss
                                    JOIN mrp_shipment_line as msl ON (msl.shipment_sale_id = mss.id)
                                    JOIN product_product as pp ON (pp.id = msl.product_id)
                                    JOIN sale_order as so ON (so.id = mss.sale_id)
                                    JOIN stock_warehouse as sw ON (sw.id = so.warehouse_id)
                                WHERE mss.shipment_id = %s """, ([doc.shipment_id.id]))
            weight_tot = 0
            if self._cr.rowcount:
                weight_tot = self._cr.fetchall()

            self._cr.execute("""SELECT ROUND(CAST(SUM(pp.volume * msl.quantity_shipped)AS NUMERIC),2)
                                FROM mrp_shipment_sale as mss
                                    JOIN mrp_shipment_line as msl ON (msl.shipment_sale_id = mss.id)
                                    JOIN product_product as pp ON (pp.id = msl.product_id)
                                    JOIN sale_order as so ON (so.id = mss.sale_id)
                                    JOIN stock_warehouse as sw ON (sw.id = so.warehouse_id)
                                WHERE mss.shipment_id = %s """, ([doc.shipment_id.id]))
            volume_tot = 0
            if self._cr.rowcount:
                volume_tot = self._cr.fetchall()
            # DATOS DEL VIAJE FLETE POR PEDIDO
            self._cr.execute("""SELECT SUM(((sol.freight_amount / sol.product_uom_qty) * msl.quantity_shipped)* so.rate_mex)
                                FROM mrp_shipment_sale as mss
                                    JOIN mrp_shipment_line as msl ON (msl.shipment_sale_id = mss.id)
                                    JOIN sale_order_line as sol ON (sol.id = msl.order_line_id)
                                    JOIN sale_order as so ON (so.id = sol.order_id)
                                    JOIN stock_warehouse as sw ON (sw.id = so.warehouse_id)
                                WHERE mss.shipment_id = %s """, ([doc.shipment_id.id]))
            flete_pedido_tot = 0
            if self._cr.rowcount:
                flete_pedido_tot = self._cr.fetchall()

            totales[doc.id][ship].append({
                                         'peso_tot': weight_tot,
                                         'volume_tot': volume_tot,
                                         'flete_pedido_tot': flete_pedido_tot,
                                         })
            travel[doc.id]['Empresa'] = self.env.user.company_id.name
            self._cr.execute("""SELECT rc.name
                                FROM tms_travel as tt
                                JOIN res_users as ru ON tt.user_id = ru.id
                                JOIN res_company as rc ON ru.company_id = rc.id
                                WHERE tt.id = %s """, ([doc.id]))
            travel[doc.id]['Fletera'] = False
            if self._cr.rowcount:
                results = self.env.cr.dictfetchall()
                for line in results:
                    travel[doc.id]['Fletera'] = line.get('name')
        docargs = {
            'doc_ids': docids,
            'docs': travel_var,
            'nombre_usuario': nombre_usuario,
            #'doc_model': report.model,
            'doc_model': self.model,
            'travel': travel,
            'travel_operator': travel_operator,
            'concatena': concatena,
            'datos_viaje': datos_viaje,
            'totales': totales,
        }
        #return report_obj.render('flete_gebesa.report_travel_instructions_2', docargs)
        return docargs
