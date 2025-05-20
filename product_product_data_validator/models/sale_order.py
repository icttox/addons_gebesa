# -*- coding: utf-8 -*-
# Copyright 2017, Cesar Barron Bautista
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
# import requests
# from xml.dom.minidom import parseString
# from odoo import tools
# import traceback
# from unidecode import unidecode


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    commitment_date = fields.Datetime(
        'Requested Date',
        readonly=False, states={}, copy=False,
        help="Date by which the customer has requested the items to be "
             "delivered.\n"
             "When this Order gets confirmed, the Delivery Order's "
             "expected date will be computed based on this date and the "
             "Company's Security Delay.\n"
             "Leave this field empty if you want the Delivery Order to be "
             "processed as soon as possible. In that case the expected "
             "date will be computed using the default method: based on "
             "the Product Lead Times and the Company's Security Delay.")

    @api.multi
    def action_confirm(self):
        for order in self:
            if order.company_id.is_manufacturer:
                # resws = order._product_data_validation()
                resws2 = order.product_data_validation2()

                if resws2 != 'OK':
                    raise ValidationError('Este pedido no podra ser aprobado  \
                        debido a errores de configuracion \
                        en los productos que ocasionarian \
                        excepciones, se ha enviado un correo detallado a los \
                        interesados.')
            elif self.company_id.country_id != self.env.ref('base.mx'):
                error = ""
                product_dup = self.do_search_multi_product_same_price()
                for product in product_dup:
                    error += u"""El producto [%s]  %s se repite en el pedido con diferente precio unitario o descuento
                    """ % (product[1], product[0])
                if error != "":
                    raise ValidationError(error)

        return super().action_confirm()

    # @api.multi
    # def _product_data_validation(self):
    #     """
    #     @params fdata : File.xml codification in base64
    #     """
    #     # import pdb
    #     # pdb.set_trace()

    #     for order in self:
    #         items = ""
    #         for line in order.order_line:
    #             items += "'" + line.product_id.default_code + "',"

    #         url = 'http://148.244.148.218:8089/validaOdoo/Service1.asmx'

    #         # ejecuta query
    #         headers = {
    #             'Content-Type': "text/xml; charset=utf-8",
    #             'SOAPAction': "http://tempuri.org/validaOdoo",
    #             'Host': "148.244.148.218",
    #             'POST': "/validaOdoo/Service1.asmx HTTP/1.1"
    #         }

    #         encoding = "utf-8"

    #         # order.client_order_ref.decode(encoding)
    #         # order.partner_id.name.decode(encoding)
    #         OC = unidecode(order.client_order_ref).encode("ascii")
    #         Cliente = unidecode(order.partner_id.name).encode("ascii")
    #         Pais = unidecode(order.partner_id.country_id.code).encode("ascii")

    #         msg = '<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-'
    #         msg += 'instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
    #         msg += 'xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
    #         msg += '<soap:Body>'
    #         msg += '<validaOdoo xmlns="http://tempuri.org/">'
    #         msg += '<articulos>' + items[:-1] + '</articulos>'
    #         msg += '<folio>' + order.name + '</folio>'
    #         msg += '<internalId>' + str(order.id) + '</internalId>'
    #         msg += '<OC><![CDATA[' + OC + ']]></OC>'
    #         msg += '<Cliente><![CDATA[' + Cliente + ']]></Cliente>'
    #         msg += '<PaisCli>' + Pais + '</PaisCli>'
    #         msg += '</validaOdoo>'
    #         msg += '</soap:Body>'
    #         msg += '</soap:Envelope>'

    #         try:
    #             response = requests.request(
    #                 "POST",
    #                 url,
    #                 data=msg,
    #                 headers=headers
    #             )

    #             # import pdb
    #             # pdb.set_trace()
    #             print('ValidaOdoProductResponse: ' + response.text)
    #             resultados_mensaje = response.content
    #             dom = parseString(resultados_mensaje)
    #             nodo = dom.getElementsByTagName('validaOdooResult')
    #             res = nodo[0].firstChild.nodeValue
    #             mensaje = res.split('|')
    #         except Exception as e:
    #             error = tools.ustr(traceback.format_exc())
    #             error = error + ' ResponsoServer: ' + response.text
    #             print(error)
    #             raise ValidationError(('Ocurrio un error al validar \
    #                                   los datos favor de notificar \
    #                                   al Administrador del sistema: %s') % (error))
    #     return mensaje

    @api.multi
    def product_data_validation2(self):
        """
        @params fdata : File.xml codification in base64
        """
        mail_obj = self.env['mail.mail']
        res = 'OK'

        for order in self:
            if not order.company_id.is_manufacturer:
                continue
            table = ""
            code_products = order.mapped('order_line').mapped(
                'product_id').mapped('default_code')
            code_products = "".join("'" + e + "'," for e in code_products)
            code_products = code_products[:len(code_products) - 1]
            self._cr.execute(
                """WITH RECURSIVE bom_detall(prodid, code, name, qty, bom,
                    bomparent,bom_type, route, ruta, reorder, costo_det,
                    costo_prod, numprovs, prod_type, ubidet, ubidetid, almdet,
                    almdetid, bom_alm, bom_almid, con, con_bom) AS (
                   SELECT pp.id, pp.default_code,
                    CASE WHEN pp.individual_name IS NULL
                     THEN pt.name ELSE pp.individual_name END,
                    ROUND(mb.product_qty, 6), mb.id, 0, mb.type, mr.name,
                    (SELECT string_agg(slr2.name, ', ')
                     FROM stock_route_product srp2
                     LEFT JOIN stock_location_route slr2
                      ON slr2.id = srp2.route_id
                     WHERE srp2.product_id = pt.id), swo.name,
                    (SELECT SUM(ip2.value_float * mbl2.product_qty)
                     FROM mrp_bom_line mbl2
                     JOIN product_product pp2 ON pp2.id = mbl2.product_id
                     JOIN ir_property ip2 ON ip2.fields_id = 2804
                      AND ip2.company_id = %s AND
                      ip2.res_id = concat('product.product,',pp2.id)
                     WHERE mbl2.bom_id = mb.id),
                    (SELECT value_float FROM ir_property ip
                     WHERE ip.fields_id = 2804
                      AND ip.company_id = %s
                      AND ip.res_id = concat('product.product,',pp.id)),
                    (SELECT COUNT(id) FROM product_supplierinfo psi
                     WHERE psi.product_tmpl_id = pt.id /*AND psi.name != 1*/), pt.type,
                    CAST('' AS TEXT), 0, CAST('' AS TEXT), 0, sw2.name,
                    sw2.id, 1, CAST(mb.id AS TEXT)
                   FROM product_product AS pp
                   INNER JOIN product_template AS pt
                    ON pp.product_tmpl_id = pt.id
                   LEFT JOIN stock_warehouse_orderpoint AS swo
                    ON swo.product_id = pp.id
                   LEFT JOIN mrp_bom AS mb ON pp.id = mb.product_id
                    AND mb.active = True
                   LEFT JOIN stock_warehouse AS sw2 ON sw2.id = mb.warehouse_id
                   LEFT JOIN mrp_routing mr ON mr.id = mb.routing_id
                   WHERE pp.default_code in (%s)
                   UNION SELECT pp.id, pp.default_code,
                    CASE WHEN pp.individual_name IS NULL
                     THEN pt.name ELSE pp.individual_name END,
                    ROUND(mbl.product_qty * bd.qty, 6), mb.id, bom,
                    mb.type, mr.name,
                    (SELECT string_agg(slr2.name, ', ')
                     FROM stock_route_product srp2
                     LEFT JOIN stock_location_route slr2
                      ON slr2.id = srp2.route_id
                     WHERE srp2.product_id = pt.id),
                    swo.name,
                    (SELECT SUM(ip2.value_float * mbl2.product_qty)
                     FROM mrp_bom_line mbl2
                     JOIN product_product pp2 ON pp2.id = mbl2.product_id
                     JOIN ir_property ip2 ON ip2.fields_id = 2804
                      AND ip2.company_id = %s
                      AND ip2.res_id = CONCAT('product.product,',pp2.id)
                     WHERE mbl2.bom_id = mb.id),
                    (SELECT value_float FROM ir_property ip
                     WHERE ip.fields_id = 2804
                     AND ip.company_id = %s
                     AND ip.res_id = CONCAT('product.product,',pp.id)),
                    (SELECT COUNT(id) FROM product_supplierinfo psi
                     WHERE psi.product_tmpl_id = pt.id),
                    pt.type, sl.name, sl.id, sw.name, sw.id, sw3.name, sw3.id,
                    con + 1, CONCAT(bd.con_bom, ' - ' ,CAST(mb.id AS TEXT))
                   FROM mrp_bom_line as mbl
                   INNER JOIN stock_location sl ON sl.id = mbl.location_id
                   INNER JOIN stock_warehouse sw
                    ON sw.id = sl.stock_warehouse_id
                   INNER JOIN bom_detall AS bd ON mbl.bom_id = bd.bom
                   INNER JOIN product_product AS pp ON mbl.product_id = pp.id
                   INNER JOIN product_template AS pt
                    ON pp.product_tmpl_id = pt.id
                   LEFT JOIN stock_warehouse_orderpoint AS swo
                    ON swo.product_id = pp.id
                   LEFT JOIN mrp_bom AS mb ON pp.id = mb.product_id
                    AND mb.active = True
                   LEFT JOIN mrp_routing mr ON mr.id = mb.routing_id
                   LEFT JOIN stock_warehouse AS sw3
                    ON sw3.id = mb.warehouse_id)
                   SELECT con, bom, bomparent, code, name,bom_type,
                    route, ruta, reorder, costo_det, costo_prod,
                    numprovs, prod_type, almdet, almdetid, ubidet,
                    ubidetid, bom_alm, bom_almid, prodid
                   FROM bom_detall ORDER BY con_bom, bom""" %
                (order.company_id.id, order.company_id.id, code_products,
                    order.company_id.id, order.company_id.id))
            if self._cr.rowcount:
                details = self._cr.fetchall()
                # Si se compra, debe tener Make To Order o Punto de Reorden
                # Temporary commented
                # table += self.do_search_bad_stock_route(details)
                # Tiene Lista de Materiales pero no tiene Ruta de producción
                table += self.do_search_bad_prod_route(details)
                # Tiene Make To Order pero, No tiene Comprar, ni Fabricar
                table += self.do_search_bad_stock_route2(details)
                # Tiene Fabricar pero, No tiene Make To Order
                table += self.do_search_bad_stock_route3(details)
                # Tiene Fabricar pero, No tiene una lista de materiales
                table += self.do_search_bad_stock_route22(details)
                # No Tiene Absolutamente nada de Ruta de Inventarios
                table += self.do_search_bad_stock_route4(details)
                # Tiene ruta para fabricar pero no para traspasar
                table += self.do_search_bad_stock_route5(details)
                # Tiene ruta (Inventarios) para fabricar Metal pero en su
                # lista de materiales tiene ruta de producción de otra planta
                table += self.do_search_bad_stock_route6(details)
                # Tiene ruta (Inventarios) para fabricar Cajas pero en su
                # lista de materiales tiene ruta de producción de otra planta
                table += self.do_search_bad_stock_route7(details)
                # Tiene ruta (Inventarios) para fabricar Madera pero en su
                # lista de materiales tiene ruta de producción de otra planta
                table += self.do_search_bad_stock_route8(details)
                # Tiene ruta (Inventarios) para fabricar Silleria pero en su
                # lista de materiales tiene ruta de producción de otra planta
                table += self.do_search_bad_stock_route9(details)
                # No coincide la ruta de fabricación con el almacen del BoM
                table += self.do_search_bad_stock_route10(details)
                # No coincide la ruta de fabricación con el almacen del BoM
                table += self.do_search_bad_stock_route11(details)
                # No coincide la ruta de fabricación con el almacen del BoM
                table += self.do_search_bad_stock_route12(details)
                # No coincide la ruta de fabricación con el almacen del BoM
                table += self.do_search_bad_stock_route13(details)
                # Se solicita estos productos a A-MP pero se fabrican en planta
                # Metal
                table += self.do_search_bad_stock_route14(details)
                # Se solicita estos productos a B-MP pero se fabrican en planta
                # Madera
                table += self.do_search_bad_stock_route15(details)
                # Se solicita estos productos a D-MP pero se fabrican en planta
                # Silleria
                table += self.do_search_bad_stock_route16(details)
                # Se solicita estos productos a F-MP pero se fabrican en planta
                # Cajas de Cartón
                table += self.do_search_bad_stock_route17(details)
                # Valida integridad de los costos
                # table += self.do_search_bad_stock_route18(details)
                # Si se compra, debe tener Al menos un proveedor
                table += self.do_search_bad_stock_route19(details)
                # Tipo de producto debe ser Product
                table += self.do_search_bad_stock_route20(details)
                # Vaida que tenga "Bajo pedido interno"
                table += self.do_search_bad_stock_route21(details)
            # Verifica que todos los productos tenga packing
            # table += order.do_search_packing(code_products)
            # Verifica que solo tenga una lista de materiales y el costo de la
            # lista de materiales sea igual al del producto
            self._cr.execute(
                """SELECT pt.name, pp.default_code, pp.id,
                       ROUND(CAST(COALESCE(ip.value_float, 0.00) AS NUMERIC), 2) as costo,
                       COUNT(DISTINCT mb.id),
                       ROUND(CAST(SUM(mbl.product_qty * COALESCE(ip2.value_float, 0.00)) AS NUMERIC), 2)
                   FROM product_template pt
                   JOIN product_product AS pp ON pp.product_tmpl_id = pt.id
                   LEFT JOIN ir_property AS ip ON CONCAT('product.product,',pp.id) = ip.res_id
                       AND ip.name = 'standard_price' AND ip.fields_id = 2804
                       AND ip.company_id = %s
                   LEFT JOIN mrp_bom AS mb ON pp.id = mb.product_id
                   LEFT JOIN mrp_bom_line AS mbl ON mb.id = mbl.bom_id
                   LEFT JOIN ir_property AS ip2 ON CONCAT('product.product,',mbl.product_id) = ip2.res_id
                       AND ip2.name = 'standard_price' AND ip2.fields_id = 2804
                       AND ip2.company_id = %s
                   WHERE pp.default_code IN (%s) AND mb.active IS TRUE
                   GROUP BY pp.id,pt.id,ip.id""" %
                (order.company_id.id, order.company_id.id, code_products))
            if self._cr.rowcount:
                for product in self._cr.fetchall():
                    if int(product[4] > 1):
                        table += u"""
                            <tr>
                                <td style=" border: 1px solid #A24689;">
                                    Este artículo tiene mas de una lista de materiales
                                </td>
                                <td style=" border: 1px solid #A24689;">
                                    <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                    [%s]  %s</a>
                                </td>
                            </tr>
                        """ % (product[2], product[1], product[0])
                    elif float(product[3]) != float(product[5]):
                        table += u"""
                            <tr>
                                <td style=" border: 1px solid #A24689;">
                                    El costo de articulo es diferente al costo en la lista de materiales
                                </td>
                                <td style=" border: 1px solid #A24689;">
                                    <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                    [%s]  %s</a>
                                </td>
                            </tr>
                        """ % (product[2], product[1], product[0])
            # Verifica que los productos tengan una clasificacion del SAT
            self._cr.execute(
                """SELECT pt.name, pp.default_code, pp.id
                   FROM product_template pt
                   JOIN product_product pp ON pp.product_tmpl_id = pt.id
                   WHERE pt.l10n_mx_edi_code_sat_id IS NULL
                   AND pp.default_code IN (%s)""" %
                (code_products))
            if self._cr.rowcount:
                for product in self._cr.fetchall():
                    table += u"""
                        <tr>
                            <td style=" border: 1px solid #A24689;">
                                Este artículo no tiene una clasificación del SAT, El pedido no podrá ser facturado
                            </td>
                            <td style=" border: 1px solid #A24689;">
                                <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                    [%s]  %s
                                </a>
                            </td>
                        </tr>
                    """ % (product[2], product[1], product[0])
            self._cr.execute(
                """WITH RECURSIVE mbl_uom_distict(name, code, product_id, bom_id, uom_pt, uom_cat_pt, uom_mbl, uom_cat_mbl) AS(
                    SELECT CASE WHEN pp.individual_name IS NULL THEN pt.name ELSE pp.individual_name END,
                        pp.default_code, pp.id, mb.id, pt.uom_id, uom.category_id, pt.uom_id, uom.category_id
                    FROM product_template pt
                    JOIN product_product pp ON pp.product_tmpl_id = pt.id
                    JOIN uom_uom AS uom ON pt.uom_id = uom.id
                    LEFT JOIN mrp_bom mb on pp.id = mb.product_id
                    WHERE pp.default_code IN (%s)
                    UNION SELECT CASE WHEN pp.individual_name IS NULL THEN pt.name ELSE pp.individual_name END,
                        pp.default_code, pp.id, mb.id, pt.uom_id, uom_pt.category_id, mbl.product_uom_id, uom_mbl.category_id
                    FROM mbl_uom_distict AS mud
                    LEFT JOIN mrp_bom AS mb on mud.product_id = mb.product_id
                    LEFT JOIN mrp_bom_line AS mbl on mb.id = mbl.bom_id
                    LEFT JOIN uom_uom AS uom_mbl ON mbl.product_uom_id = uom_mbl.id
                    LEFT JOIN product_product pp ON mbl.product_id = pp.id
                    LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                    LEFT JOIN uom_uom AS uom_pt ON pt.uom_id = uom_pt.id
                    LEFT JOIN mrp_bom AS mb2 on mbl.product_id = mb2.product_id)
                SELECT name, code, bom_id FROM mbl_uom_distict WHERE uom_cat_pt != uom_cat_mbl""" %
                (code_products))
            if self._cr.rowcount:
                for product in self._cr.fetchall():
                    table += u"""
                         <tr>
                            <td style=" border: 1px solid #A24689;">
                                La categoria de la unidad de medida de este producto es distinta a la del bom line
                            </td>
                            <td style=" border: 1px solid #A24689;">
                                <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=mrp.bom&action=396&menu_id=277">
                                    [%s]  %s
                                </a>
                            </td>
                        </tr>
                    """ % (product[2], product[1], product[0])
            pais_cliente = order.partner_id.country_id.code
            if pais_cliente != "MX":
                self._cr.execute(
                    """SELECT pt.name, pp.default_code, pp.id
                       FROM product_template pt
                       JOIN product_product pp ON pp.product_tmpl_id = pt.id
                       WHERE pt.l10n_mx_edi_tariff_fraction_id IS NULL
                       AND pp.default_code IN (%s)""" %
                    (code_products))
                if self._cr.rowcount:
                    for product in self._cr.fetchall():
                        table += u"""
                             <tr>
                                <td style=" border: 1px solid #A24689;">
                                    Este artículo no tiene una Partida Arancelaria válida, El pedido no podrá ser facturado a clientes de %s
                                </td>
                                <td style=" border: 1px solid #A24689;">
                                    <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                        [%s]  %s
                                    </a>
                                </td>
                            </tr>
                        """ % (pais_cliente, product[2], product[1], product[0])
                self._cr.execute(
                    """SELECT pt.name, pp.default_code, pp.id
                       FROM product_template pt
                       JOIN product_product pp ON pp.product_tmpl_id = pt.id
                       WHERE pt.l10n_mx_edi_umt_aduana_id IS NULL
                       AND pp.default_code IN (%s)""" %
                    (code_products))
                if self._cr.rowcount:
                    for product in self._cr.fetchall():
                        table += u"""
                             <tr>
                                <td style=" border: 1px solid #A24689;">
                                    Este artículo no tiene una Unidad de medida para aduana válida, El pedido no podrá ser facturado a clientes de %s
                                </td>
                                <td style=" border: 1px solid #A24689;">
                                    <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                        [%s]  %s
                                    </a>
                                </td>
                            </tr>
                        """ % (pais_cliente, product[2], product[1], product[0])
                # Valida que la unidad de media de la aduana y
                # la fraccion arancelaria tengan el mismo codigo fiscal
                self._cr.execute(
                    """SELECT pt.name, pp.default_code, pp.id,
                        uu.name AS uom, uu.fiscal_code,
                        CONCAT(tf.code, ' ', tf.name),
                        tf.uom_code
                    FROM sale_order AS so
                    JOIN sale_order_line AS sol ON so.id = sol.order_id
                    JOIN product_product AS pp ON sol.product_id = pp.id
                    JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                    LEFT JOIN uom_uom AS uu ON pt.l10n_mx_edi_umt_aduana_id = uu.id
                    LEFT JOIN l10n_mx_edi_tariff_fraction AS tf ON pt.l10n_mx_edi_tariff_fraction_id = tf.id
                    WHERE so.id = %s
                        AND tf.id IS NOT NULL
                        AND uu.id IS NOT NULL
                        AND uu.fiscal_code != tf.uom_code
                    GROUP BY pp.id,pt.id,uu.id,tf.id
                    ORDER BY pp.default_code
                    """ % (str(order.id)))
                if self._cr.rowcount:
                    for product in self._cr.fetchall():
                        table += u"""
                            <tr>
                                <td style=" border: 1px solid #A24689;">
                                    La unidad de medida de la fraccion arancelaria(%s) no corresponde con la unidad de medida Aduana(%s) del producto
                                </td>
                                <td style=" border: 1px solid #A24689;">
                                    <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                        [%s]  %s
                                    </a>
                                </td>
                            </tr>
                        """ % (product[5], product[3], product[2], product[1], product[0])
            # Valida que la familia y la ruta de produccion del producto coincida
            self._cr.execute(
                """
                    SELECT
                        pt.name,pp.default_code,pp.id,pf.name,slr.name
                    FROM sale_order AS so
                    LEFT JOIN sale_order_line AS sol ON so.id = sol.order_id
                    LEFT JOIN product_product AS pp ON sol.product_id = pp.id
                    LEFT JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                    LEFT JOIN product_family as pf on pf.id = pt.family_id
                    LEFT JOIN stock_route_product srp ON srp.product_id = pt.id
                    LEFT JOIN stock_location_route slr ON slr.id = srp.route_id
                    WHERE so.id = %s
                        AND slr.name LIKE 'Fabri%%' AND CASE
                            WHEN slr.name = 'Fabricación Metal' THEN pf.name NOT IN ('Cajas de Herramientas', 'Mamparas', 'Metal', 'Metálicos', 'Varios', 'Arneses - Multicontactos')
                            WHEN slr.name = 'Fabricación Madera' THEN pf.name NOT IN ('Chapa', 'Laminados', 'Madera', 'Varios')
                            WHEN slr.name = 'Fabricación Sillería' THEN pf.name NOT IN ('Silleria', 'Silleria Armado', 'Sillería Compra-Venta', 'Sillería Fabricación', 'Varios')
                            WHEN slr.name = 'Fabricación Cajas de Cartón' THEN  pf.name NOT IN ('Cajas De Carton', 'Varios')
                            END
                    GROUP BY pp.id,pt.id,pf.id,slr.id
                    ORDER BY pf.name,slr.name,pp.default_code
                """ % (str(order.id)))
            if self._cr.rowcount:
                for product in self._cr.fetchall():
                    table += u"""
                         <tr>
                            <td style=" border: 1px solid #A24689;">
                                No coincide la familia (%s) con la ruta de inventarios (%s)
                            </td>
                            <td style=" border: 1px solid #A24689;">
                                <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                    [%s]  %s
                                </a>
                            </td>
                        </tr>
                    """ % (product[3], product[4], product[2], product[1], product[0])
            # Valida que no se repita el producto con el mismo precio unitario
            product_dup = self.do_search_multi_product_same_price()
            for product in product_dup:
                table += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            El producto [%s]  %s se repite en el pedido con diferente precio unitario o descuento
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="https://erp.portalgebesa.com/web#id=%s&action=412&model=sale.order&view_type=form&menu_id=1686">
                                %s
                            </a>
                        </td>
                    </tr>
                """ % (product[1], product[0], self.id, self.name)
            if table != "":
                self.env.cr.rollback()
                res = 'Error'
                body_mail = u"""
                    <div summary="o_mail_notification" style="padding:0px; width:700px; margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                        <table cellspacing="0" cellpadding="0" style="width:700px; border-collapse:collapse; background:inherit; color:inherit">
                            <tbody><tr>
                                <td valign="center" width="370px" style="padding:5px 10px 5px 5px;font-size: 16px">
                                    <p>Falta informacion en productos al intentar validar el pedido %s del Cliente %s , orden de compra: %s.</p>
                                </td>
                                <td valign="center" align="right" width="270px" style="padding:5px 15px 5px 10px; font-size: 12px;">
                                    <p>
                                    <strong>Sent by</strong>
                                    <a href="http://erp.portalgebesa.com" style="text-decoration:none; color: #a24689;">
                                        <strong>%s</strong>
                                    </a>
                                    <strong>using</strong>
                                    <a href="https://www.odoo.com" style="text-decoration:none; color: #a24689;"><strong>Odoo</strong></a>
                                    </p>
                                </td>
                            </tr>
                        </tbody></table>
                    </div>
                    <div style="padding:0px; width:700px; margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                        <table cellspacing="0" cellpadding="0" style="vertical-align:top; padding:0px; border-collapse:collapse; background:inherit; color:inherit">
                            <tbody><tr>
                                <td valign="top" style="width:700px; padding:5px 10px 5px 5px;">
                                    <div>
                                        <hr width="100%%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0;margin:15px auto;padding:0">
                                    </div>
                                </td>
                            </tr></tbody>
                        </table>
                    </div>
                    <div style="padding:0px; width:700px; margin:0 auto; background: #FFFFFF repeat top /100%%;color:#777777">
                        <table style="border-collapse:collapse; margin: 0 auto; width:700px; background:inherit; color:inherit">
                            <tbody><tr>
                                <th style="border: 1px solid #A24689;background-color: #A24689;Color: #FFFFFF">Error</th>
                                <th style="border: 1px solid #A24689;background-color: #A24689;Color: #FFFFFF">Artículo</th>
                            </tr>
                            %s
                            </tbody>
                        </table>
                    </div>
                """ % (order.name, order.partner_id.name, order.client_order_ref, self.env.user.company_id.name, table)
                destinatarios = self.env['ir.config_parameter'].sudo().get_param(
                    'product_data_validator.sale_email', 'sistemas@gebesa.com')
                mail = mail_obj.create({
                    'subject': 'Falta informacion en productos al intentar validar el pedido ' + order.name,
                    'email_to': destinatarios,
                    'headers': "{'Return-Path': u'odoo@gebesa.com'}",
                    'body_html': body_mail,
                    'auto_delete': True,
                    'message_type': 'comment',
                    'model': 'sale.order',
                    'res_id': order.id,
                })
                mail.send(auto_commit=True)
                order.message_post(body=u"""<table style="border-collapse:collapse; margin: 0 auto; width:700px; background:inherit; color:inherit">
                    <tbody><tr>
                        <th style="border: 1px solid #A24689;background-color: #A24689;Color: #FFFFFF">Error</th>
                        <th style="border: 1px solid #A24689;background-color: #A24689;Color: #FFFFFF">Artículo</th>
                    </tr>
                    %s
                    </tbody></table>""" % (table))
                self.env.cr.commit()
        return res

    # Si se compra, debe tener Make To Order o Punto de Reorden
    def do_search_bad_stock_route(self, details):
        error = u""
        for product in details:
            if "Make To Order" not in product[7] and "Buy" in product[7] and product[8] is None:
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            Este Artículo es de compra pero no tiene Máximos y Mínimos ni esta configurado Bajo Pedido, Odoo no lo considerará para abastecimientos
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # Tiene Lista de Materiales pero no tiene Ruta de producción
    def do_search_bad_prod_route(self, details):
        error = u""
        for product in details:
            if product[1] is None and product[2] == 0:
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            Este Artículo no tiene una lista de materiales, Odoo no sabrá como ejecutar la Orden de Fabricación
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
            if product[5] is not None and "normal" in str(product[5]) and product[6] is None:
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            Este Artículo no tiene una Ruta de producción en su lista de materiales, Odoo no sabrá donde ejecutar la Orden de Fabricación
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # Tiene Make To Order pero, No tiene Comprar, ni Fabricar
    def do_search_bad_stock_route2(self, details):
        error = u""
        for product in details:
            if "Make To Order" in product[7] and "Buy" not in product[7] and u"Fabricación" not in product[7]:
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            Este Artículo está marcado como Bajo Pedido pero no tiene configurado si se compra o se fabrica, Odoo no sabrá de donde abastecerse de este artículo
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # Tiene Fabricar pero, No tiene Make To Order
    def do_search_bad_stock_route3(self, details):
        error = u""
        for product in details:
            if "Make To Order" not in product[7] and u"Fabricación" in product[7]:
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            Este Artículo está marcado para Fabricar pero no como Bajo Pedido, Odoo no lo mandará a fabricar
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # No Tiene Absolutamente nada de Ruta de Inventarios
    def do_search_bad_stock_route4(self, details):
        error = u""
        for product in details:
            if product[7] is None:
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            Este Artículo no tiene configurada ninguna ruta de inventarios, Odoo no lo considerará para abastecimientos
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # Tiene ruta para fabricar pero no para traspasar
    def do_search_bad_stock_route5(self, details):
        error = u""
        for product in details:
            if "proveer producto" not in product[7] and u"Fabricación" in product[7]:
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            Este Artículo está marcado para fabricar pero debe poder traspasarse a las demás plantas, Odoo no lo considerará para traspasos entre almacenes
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # Tiene ruta (Inventarios) para fabricar Metal pero en su lista de
    # materiales tiene ruta de producción de otra planta
    def do_search_bad_stock_route6(self, details):
        error = u""
        for product in details:
            if "A-" not in str(product[6]) and "normal" in str(product[5]) and u"Fabricación Metal" in product[7]:
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            Este Artículo está configurado para fabricarse en Metal pero su detalle de fabricación es de otra planta, Odoo lo enviará a excepción de abastecimiento
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # Tiene ruta (Inventarios) para fabricar Cajas pero en su lista de
    # materiales tiene ruta de producción de otra planta
    def do_search_bad_stock_route7(self, details):
        error = u""
        for product in details:
            if "F-" not in str(product[6]) and "normal" in str(product[5]) and u"Fabricación Cajas de Cartón" in product[7]:
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            Este Artículo está configurado para fabricarse en Cajas de Cartón pero su detalle de fabricación es de otra planta, Odoo lo enviará a excepción de abastecimiento
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # Tiene ruta (Inventarios) para fabricar Madera pero en su lista de
    # materiales tiene ruta de producción de otra planta
    def do_search_bad_stock_route8(self, details):
        error = u""
        for product in details:
            if "B-" not in str(product[6]) and "normal" in str(product[5]) and u"Fabricación Madera" in product[7]:
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            Este Artículo está configurado para fabricarse en Madera pero su detalle de fabricación es de otra planta, Odoo lo enviará a excepción de abastecimiento
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # Tiene ruta (Inventarios) para fabricar Sillería pero en su lista de
    # materiales tiene ruta de producción de otra planta
    def do_search_bad_stock_route9(self, details):
        error = u""
        for product in details:
            if "D-" not in str(product[6]) and "normal" in str(product[5]) and u"Fabricación Sillería" in product[7]:
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            Este Artículo está configurado para fabricarse en Silleria pero su detalle de fabricación es de otra planta, Odoo lo enviará a excepción de abastecimiento
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # Tiene ruta Producción Metal el almacen de la lista de materiales
    # pero la Ruta de Fab tiene otra planta
    def do_search_bad_stock_route10(self, details):
        error = u""
        for product in details:
            if "A-" in str(product[6]) and "Metal" not in product[17]:
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            No coinciden la Ruta de Fabricación con el Almacén %s %s de la Lista de Materiales, Odoo lo enviará a excepción de abastecimiento
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[17], product[6], product[19], product[3], product[4])
        return error

    # Tiene ruta Producción Madera el almacen de la lista de materiales
    # pero la Ruta de Fab tiene otra planta
    def do_search_bad_stock_route11(self, details):
        error = u""
        for product in details:
            if "B-" in str(product[6]) and "Madera" not in product[17]:
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            No coinciden la Ruta de Fabricación con el Almacén %s %s de la Lista de Materiales, Odoo lo enviará a excepción de abastecimiento
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[17], product[6], product[19], product[3], product[4])
        return error

    # Tiene ruta Producción Silleria el almacen de la lista de materiales
    # pero la Ruta de Fab tiene otra planta
    def do_search_bad_stock_route12(self, details):
        error = u""
        for product in details:
            if "D-" in str(product[6]) and "Silleria" not in product[17]:
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            No coinciden la Ruta de Fabricación con el Almacén %s %s de la Lista de Materiales, Odoo lo enviará a excepción de abastecimiento
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[17], product[6], product[19], product[3], product[4])
        return error

    # Tiene ruta Producción Cajas de Cartón el almacen de la lista de
    # materiales pero la Ruta de Fab tiene otra planta
    def do_search_bad_stock_route13(self, details):
        error = u""
        for product in details:
            if "F-" in str(product[6]) and u"Cajas de Cartón" not in product[17]:
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            No coinciden la Ruta de Fabricación con el Almacén %s %s de la Lista de Materiales, Odoo lo enviará a excepción de abastecimiento
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[17], product[6], product[19], product[3], product[4])
        return error

    # Se solicita estos productos a A-MP pero se fabrican en planta Metal
    def do_search_bad_stock_route14(self, details):
        error = u""
        for product in details:
            if u"Almacén de MP" in product[13] and "Metal" in product[15] and "A-" in str(product[6]):
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            Este artículo se solicita a Materia Prima pero no es una materia prima, Odoo lo enviará a excepción de abastecimiento
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # Se solicita estos productos a B-MP pero se fabrican en planta Madera
    def do_search_bad_stock_route15(self, details):
        error = u""
        for product in details:
            if u"Almacén de MP" in product[13] and "Madera" in product[15] and "B-" in str(product[6]):
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            Este artículo se solicita a Materia Prima pero no es una materia prima, Odoo lo enviará a excepción de abastecimiento
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # Se solicita estos productos a D-MP pero se fabrican en planta Silleria
    def do_search_bad_stock_route16(self, details):
        error = u""
        for product in details:
            if u"Almacén de MP" in product[13] and "Silleria" in product[15] and "D-" in str(product[6]):
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            Este artículo se solicita a Materia Prima pero no es una materia prima, Odoo lo enviará a excepción de abastecimiento
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # Se solicita estos productos a F-MP pero se fabrican en planta Cajas
    def do_search_bad_stock_route17(self, details):
        error = u""
        for product in details:
            if u"Almacén de MP" in product[13] and u"Cajas de Cartón" in product[15] and "F-" in str(product[6]):
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            Este artículo se solicita a Materia Prima pero no es una materia prima, Odoo lo enviará a excepción de abastecimiento
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # Valida integridad de los costos
    def do_search_bad_stock_route18(self, details):
        error = u""
        for product in details:
            if product[13] is not None and round(float(product[10]), 2) != round(float(product[9]), 2):
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            Este artículo tiene costo desfasado en relación con su lista de materiales, Odoo lo enviará a excepción de abastecimiento
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # Si se compra, debe tener Al menos un proveedor
    def do_search_bad_stock_route19(self, details):
        error = u""
        for product in details:
            if int(product[11]) == 0 and "Buy" in product[7]:
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            Este artículo es Materia Prima pero no tiene ningun proveedor relacionado, Odoo lo enviará a excepción de abastecimiento
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # Si se compra, debe tener Al menos un proveedor
    def do_search_bad_stock_route20(self, details):
        error = u""
        for product in details:
            if str(product[12]) != "product":
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            El tipo de producto debe ser Stockable Product, Odoo no lo considerará para los abastecimientos
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # Debe tener la ruta de bajo pedido interno
    def do_search_bad_stock_route21(self, details):
        error = u""
        for product in details:
            if "Bajo pedido interno" not in product[7]:
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            El articulo no esta marcado como "Bajo pedido interno"
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # Debe tener la ruta de bajo pedido interno
    def do_search_bad_stock_route22(self, details):
        error = u""
        for product in details:
            if "Fabricación" in product[7] and product[1] == None:
                error += u"""
                     <tr>
                        <td style=" border: 1px solid #A24689;">
                            El articulo esta marcado como fabricar pero no tiene ninguna lista de materiales
                        </td>
                        <td style=" border: 1px solid #A24689;">
                            <a href="http://erp.portalgebesa.com/web?#id=%s&view_type=form&model=product.product&action=188&menu_id=63">
                                [%s]  %s
                            </a>
                        </td>
                    </tr>
                """ % (product[19], product[3], product[4])
        return error

    # Valida que no se repita el producto con el mismo precio unitario
    def do_search_multi_product_same_price(self):
        self._cr.execute("""
            SELECT name,default_code,id,COUNT(price_unit),COUNT(discount)
            FROM (
                SELECT pt.name,pp.default_code,pp.id,sol.price_unit,sol.discount
                FROM sale_order_line AS sol
                JOIN product_product AS pp ON sol.product_id = pp.id
                JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                WHERE sol.order_id = %s AND pt.type != 'service'
                GROUP BY pp.id,pt.id,sol.price_unit,sol.discount
            ) AS agrupacion
            GROUP BY name,default_code,id HAVING COUNT(price_unit) > 1 OR COUNT(discount) > 1
        """ % (str(self.id)))
        if self._cr.rowcount:
            return self._cr.fetchall()
        return []

    # Verifica que todos los productos tenga packing
    def do_search_packing(self, code_products):
        error = u""
        self._cr.execute(
            """
            WITH RECURSIVE product_packing(origin, origin_name, product_id, code, name, product_tmpl_id, bom_id, bom_type, packing, validar, level) AS(
                SELECT
                    pp.default_code,
                    COALESCE(pp.individual_name,pp.name_template),
                    pp.id,
                    pp.default_code,
                    COALESCE(pp.individual_name,pp.name_template),
                    pp.product_tmpl_id,
                    mb.id,
                    mb.type,
                    MAX(ppl.id),
                    CASE WHEN mb.type = 'normal' OR (mb.type = 'phantom' AND MAX(ppl.id) IS NOT NULL)
                        THEN TRUE ELSE FALSE END,
                    LPAD(ROW_NUMBER () OVER ()::text, 2, '0')
                FROM product_product AS pp
                LEFT JOIN mrp_bom AS mb ON pp.id = mb.product_id AND mb.active IS TRUE
                LEFT JOIN product_packing_list AS ppl ON pp.product_tmpl_id = ppl.product_tmpl_id
                    AND ppl.active IS TRUE AND ppl.type = CASE WHEN mb.type = 'normal' THEN 'standard' ELSE 'exeption' END
                WHERE pp.default_code IN (%s)
                GROUP BY pp.id, mb.id
                UNION SELECT
                    pack.origin,
                    pack.origin_name,
                    pp.id,
                    pp.default_code,
                    COALESCE(pp.individual_name,pp.name_template),
                    pp.product_tmpl_id,
                    mb.id,
                    mb.type,
                    ppl.id,
                    CASE WHEN mb.type = 'normal'
                        THEN TRUE ELSE FALSE END,
                    CONCAT(pack.level, '-', LPAD(ROW_NUMBER () OVER ()::text, 2, '0'))
                FROM product_packing AS pack
                LEFT JOIN mrp_bom_line AS mbl ON pack.bom_id = mbl.bom_id
                LEFT JOIN product_product AS pp ON mbl.product_id = pp.id
                LEFT JOIN mrp_bom AS mb ON pp.id = mb.product_id AND mb.active IS TRUE
                LEFT JOIN product_packing_list AS ppl ON pp.product_tmpl_id = ppl.product_tmpl_id
                    AND ppl.active IS TRUE AND ppl.type = 'standard'
                WHERE pack.bom_type = 'phantom' AND (pack.packing IS NULL OR pack.packing = 0)
            )
            SELECT * FROM product_packing WHERE validar IS TRUE ORDER BY level""" %
            (code_products))
        if self._cr.rowcount:
            for product in self._cr.fetchall():
                if product[8] is None:
                    if product[0] == product[3]:
                        error += u"""
                        <tr>
                            <td style=" border: 1px solid #A24689;">
                                Este artículo no tiene un packing list, El pedido no podra ser embarcado
                            </td>
                            <td style=" border: 1px solid #A24689;">
                                <a href="http://erp.portalgebesa.com/web#min=1&limit=80&view_type=list&model=product.packing.list&action=2297&menu_id=1074">
                                    [%s]  %s
                                </a>
                            </td>
                        </tr>
                        """ % (product[3], product[4])
                    else:
                        error += u"""
                        <tr>
                            <td style=" border: 1px solid #A24689;">
                                Este artículo contenido en un kit no tiene un packing list, El pedido no podra ser embarcado
                            </td>
                            <td style=" border: 1px solid #A24689;">
                                <a href="http://erp.portalgebesa.com/web#min=1&limit=80&view_type=list&model=product.packing.list&action=2297&menu_id=1074">
                                    [%s]  %s
                                </a>
                            </td>
                        </tr>
                        """ % (product[3], product[4])
        return error
