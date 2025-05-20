# Copyright 2020, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
from odoo import models

_logger = logging.getLogger(__name__)


def copy_format(book, fmt):
    properties = [f[4:] for f in dir(fmt) if f[0:4] == 'set_']
    dft_fmt = book.add_format()
    res = book.add_format(
        {k: v for k, v in fmt.__dict__.items() if k in properties and dft_fmt.__dict__[k] != v})
    return res


class ReportSalidaMercanciasAnexo24(models.AbstractModel):
    _name = 'report.immex_gebesa.report_salida_mercancia_anexo24'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        workbook.set_properties({
            'comments': 'Created with Python and XlsxWriter from Odoo 12.0'})
        sheet = workbook.add_worksheet('Lista de Materiales')
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(90)
        bold = workbook.add_format({'bold': True})
        bold_red = workbook.add_format({
            'bold': True, 'font_color': 'red'})

        sheet.write('A1', 'REGIMEN', bold)
        sheet.write('B1', 'PEDIMENTO', bold)
        sheet.write('C1', 'ADUANA', bold)
        sheet.write('D1', 'FECHA ENTRADA', bold)
        sheet.write('E1', 'FECHA DE PAGO', bold)
        sheet.write('F1', 'CLAVE', bold)
        sheet.write('G1', 'TIPO DE CAMBIO', bold)
        sheet.write('H1', 'VALOR SEGUROS', bold)
        sheet.write('I1', 'FLETES', bold)
        sheet.write('J1', 'EMBALAJES', bold)
        sheet.write('K1', 'OTROS INCREMENTABLES', bold)
        sheet.write('L1', 'DTA', bold)
        sheet.write('M1', 'IVA MONTO MN', bold)
        sheet.write('N1', 'PREVIO', bold)
        sheet.write('O1', '% IGI', bold)
        sheet.write('P1', 'IGI MONTO MN', bold)
        sheet.write('Q1', 'MATERIAL', bold)
        sheet.write('R1', 'DESCRIPCION', bold)
        sheet.write('S1', 'CANTIDAD COMERCIAL', bold)
        sheet.write('T1', 'UM COMERCIAL', bold)
        sheet.write('U1', 'CANTIDAD TARIFA', bold)
        sheet.write('V1', 'UM TARIFA', bold)
        sheet.write('W1', 'VALOR FACTURA USD', bold)
        sheet.write('X1', 'VALOR ADUANA USD', bold)
        sheet.write('Y1', 'VALOR ADUANA MN', bold)
        sheet.write('Z1', 'PRECIO PAGADO / VALOR COMERCIAL (MN)', bold)
        sheet.write('AA1', 'RFC / TAX ID NUMERO PROVEEDOR', bold)
        sheet.write('AB1', 'VINCULACION', bold)
        sheet.write('AC1', 'FACT IMP', bold)
        sheet.write('AD1', 'FECHA FACTURA', bold)
        sheet.write('AE1', 'INCOTERM', bold)
        sheet.write('AF1', 'FRACCION', bold)
        sheet.write('AG1', 'PAIS ORIGEN', bold)
        sheet.write('AH1', 'PAIS PROVEEDOR', bold)
        sheet.write('AI1', 'CANTIDAD DESCARGA', bold)
        sheet.write('AJ1', 'SALDO', bold)
        sheet.write('AK1', 'PAIS DESTINO', bold)
        sheet.write('AL1', 'DOCUMENTO DESCARGO', bold)
        sheet.write('AM1', 'FECHA PAGO DOCUMENTO DESCARGO', bold)
        sheet.write('AN1', 'FECHA PRESENTACION', bold)
        sheet.write('AO1', 'CLAVE', bold)
        sheet.write('AP1', 'REGIMEN', bold)
        sheet.write('AQ1', 'VALOR AGREGADO MN', bold)
        sheet.write('AR1', 'VALOR USD', bold)
        sheet.write('AS1', 'VALOR COMERCIAL MN', bold)
        sheet.write('AT1', 'TIPO CAMBIO', bold)
        sheet.write('AU1', 'FACTURA', bold)
        sheet.write('AV1', 'FECHA FACTURA VENTA', bold)
        sheet.write('AW1', 'CLIENTE', bold)
        sheet.write('AX1', 'SUBCLIENTE', bold)
        sheet.write('AY1', 'PRODUCTO', bold)
        sheet.write('AZ1', 'UM COMERCIAL', bold)
        sheet.write('BA1', 'PRECIO UNITARIO', bold)
        sheet.write('BB1', 'CANTIDAD COMERCIAL EXPORTADA', bold)
        sheet.write('BC1', 'CANTIDAD TARIFA EXPORTADA', bold)
        sheet.write('BD1', 'UM TARIFA', bold)
        sheet.write('BE1', 'FRACCION ARANCELARIA', bold)
        sheet.write('BF1', 'DESCRIPCION', bold)

        rownum = 2
        partida = False
        for merc in self._get_data_pedimento(objects):
            if partida != merc[3]:
                partida = merc[3]
                lines_desc = {}
                descargue_line = self.env[
                    'l10n.mx.immex.partida.descargue.line'].search([
                        ('partida_id', '=', merc[3])])
                for des_line in descargue_line:
                    lines_desc[des_line.id] = {
                        'amount': des_line.quantity,
                        'rec': des_line
                    }
            amount = merc[23]
            for line in sorted(lines_desc.keys()):
                if lines_desc[line]['amount'] > 0 and amount > 0:

                    if amount <= lines_desc[line]['amount']:
                        amount_desc = amount
                        lines_desc[line]['amount'] -= amount
                        amount -= amount
                    else:
                        amount_desc = lines_desc[line]['amount']
                        amount -= lines_desc[line]['amount']
                        lines_desc[line]['amount'] -= lines_desc[line]['amount']

                    sheet.write('A' + str(rownum), 'ITE')
                    sheet.write('B' + str(rownum), merc[4])
                    sheet.write('C' + str(rownum), merc[5])
                    sheet.write('D' + str(rownum), merc[6])
                    sheet.write('E' + str(rownum), merc[7])
                    sheet.write('F' + str(rownum), merc[8])
                    sheet.write('G' + str(rownum), merc[9])
                    sheet.write('H' + str(rownum), merc[10])
                    sheet.write('I' + str(rownum), merc[11])
                    sheet.write('J' + str(rownum), merc[12])
                    sheet.write('K' + str(rownum), merc[13])
                    sheet.write('L' + str(rownum), merc[14])
                    sheet.write('M' + str(rownum), merc[15])
                    sheet.write('N' + str(rownum), merc[16])
                    sheet.write('O' + str(rownum), merc[17])
                    sheet.write('P' + str(rownum), merc[18])
                    sheet.write('Q' + str(rownum), merc[19])
                    sheet.write('R' + str(rownum), merc[20])
                    sheet.write('S' + str(rownum), merc[21])
                    sheet.write('T' + str(rownum), merc[22])
                    sheet.write('U' + str(rownum), merc[23])
                    sheet.write('V' + str(rownum), merc[24])
                    sheet.write('W' + str(rownum), merc[25])

                    valor_duana_mater = (merc[26] / merc[34]) * merc[35]
                    sheet.write('X' + str(rownum), valor_duana_mater / merc[9])
                    sheet.write('Y' + str(rownum), valor_duana_mater)
                    sheet.write('Z' + str(rownum), merc[26])

                    sheet.write('AA' + str(rownum), merc[27])
                    sheet.write('AB' + str(rownum), 'NO')
                    sheet.write('AC' + str(rownum), merc[28])
                    sheet.write('AD' + str(rownum), merc[29])
                    sheet.write('AE' + str(rownum), merc[30])
                    sheet.write('AF' + str(rownum), merc[31])
                    sheet.write('AG' + str(rownum), merc[32])
                    sheet.write('AH' + str(rownum), merc[33])
                    sheet.write('AI' + str(rownum), amount_desc)
                    sheet.write('AJ' + str(rownum), amount)

                    merc_sal = lines_desc[line]['rec'].descargue_id.invoice_id.mapped(
                        'factura_ids').mapped('factura_mercancia_ids').filtered(
                        lambda sal: sal.invoice_line_id.id == lines_desc[line][
                            'rec'].descargue_id.invoice_line_id.id)
                    if merc_sal:
                        merc_sal = merc_sal[0]
                        regimen = 'EXD'
                    else:
                        regimen = ''

                    sheet.write(
                        'AK' + str(rownum), (merc_sal.pedimento_id.pais or ''))
                    if not merc_sal:
                        sheet.write(
                            'AK' + str(rownum),
                            lines_desc[line]['rec'].descargue_id.invoice_id.number,
                            bold_red)
                    sheet.write(
                        'AL' + str(rownum),
                        (merc_sal.pedimento_id.pedimento_num or ''))
                    sheet.write(
                        'AM' + str(rownum),
                        (merc_sal.pedimento_id.fecha_pago_real or ''))
                    sheet.write(
                        'AN' + str(rownum),
                        (merc_sal.pedimento_id.fecha_pedimento or ''))
                    sheet.write(
                        'AO' + str(rownum),
                        (merc_sal.pedimento_id.clave_documento or ''))
                    sheet.write('AP' + str(rownum), regimen)
                    sheet.write('AQ' + str(rownum), 0.0)
                    sheet.write(
                        'AR' + str(rownum),
                        float(merc_sal.immex_invoice_id.monto_usd))
                    sheet.write(
                        'AS' + str(rownum),
                        float(merc_sal.immex_invoice_id.monto_usd) * float(
                            merc_sal.pedimento_id.tipo_cambio))
                    sheet.write(
                        'AT' + str(rownum),
                        float(merc_sal.pedimento_id.tipo_cambio))
                    sheet.write(
                        'AU' + str(rownum),
                        (merc_sal.immex_invoice_id.uuid or ''))
                    sheet.write(
                        'AV' + str(rownum),
                        (merc_sal.immex_invoice_id.fecha_facturacion or ''))
                    sheet.write(
                        'AW' + str(rownum),
                        (merc_sal.immex_invoice_id.id_fiscal_proveedor or ''))
                    sheet.write('AX' + str(rownum), '')
                    sheet.write(
                        'AY' + str(rownum),
                        (merc_sal.partida_id.materials_code or ''))
                    sheet.write(
                        'AZ' + str(rownum),
                        (merc_sal.partida_id.udm_comercial or ''))

                    sheet.write(
                        'BA' + str(rownum),
                        float(merc_sal.partida_id.precio_unitario))
                    sheet.write(
                        'BB' + str(rownum),
                        float(merc_sal.partida_id.cantidad_udm_comercial))
                    sheet.write(
                        'BC' + str(rownum),
                        float(merc_sal.partida_id.cantidad_udm_tarifa))
                    sheet.write(
                        'BD' + str(rownum),
                        (merc_sal.partida_id.udm_tarifa or ''))
                    sheet.write(
                        'BE' + str(rownum),
                        (merc_sal.partida_id.fraccion_arancelaria or ''))
                    sheet.write(
                        'BF' + str(rownum),
                        (merc_sal.partida_id.descripcion or ''))
                    rownum += 1

    def _get_data_pedimento(self, objects):
        self._cr.execute("""
            SELECT
                impe.id AS id_ped,
                impefac.id AS id_fac,
                impefacmer.id AS id_mer,
                impat.id AS id_partida,
                impe.pedimento_num AS pedimento,
                impe.clave_aduana AS aduana,
                impe.fecha_pedimento AT TIME ZONE 'UTC' AT TIME ZONE 'America/Mexico_City'  AS fecha_entrada,
                impe.fecha_pago_real AT TIME ZONE 'UTC' AT TIME ZONE 'America/Mexico_City' AS fecha_pago,
                impe.clave_documento AS clave,
                CAST(impe.tipo_cambio AS FLOAT) AS tipo_cambio,
                CAST(impe.total_seguros AS FLOAT) AS total_seguros,
                CAST(impe.total_flete AS FLOAT) AS total_flete,
                CAST(impe.total_embalages AS FLOAT) AS total_embalages,
                CAST(impe.total_otros_inc AS FLOAT) AS total_otros_inc,
                ped_cont.DTA,
                part_cont.iva_mn,
                ped_cont.PREVIO,
                CASE WHEN part_tasas.per_igi != '' THEN part_tasas.per_igi ELSE '0.00'END AS per_igi,
                part_cont.monto_igi,
                pp.default_code AS material,
                impefacmer.descripcion AS descripcion,
                impefacmer.cantidad AS cantidad_comercial,
                impat.udm_comercial AS um_comercial,
                (impefacmer.cantidad / CAST(impat.cantidad_udm_comercial AS FLOAT)) * CAST(impat.cantidad_udm_tarifa AS FLOAT) AS cantidad_tarifa,
                impat.udm_tarifa AS um_tarifa,
                impefacmer.valor_total AS valor_comercial_material,
                impefacmer.valor_total * CAST(impe.tipo_cambio AS FLOAT) AS valor_comercial_mx_material,
                impe.rfc_contribuyente,

                impefac.uuid AS factura,
                CAST(impefac.fecha_facturacion AS DATE) AS fecha_factura,
                impefac.termino_facturacion AS incoterm,
                impat.fraccion_arancelaria AS fraccion_arranc,
                impat.pais AS pais_origen,
                impat.pais_extranjero AS pais_proveedor,
                sum_impefac.sum_usd * CAST(impe.tipo_cambio AS FLOAT) AS valor_comercial_mxn_ped,
                (sum_impefac.sum_usd * CAST(impe.tipo_cambio AS FLOAT)) + (CAST(impe.total_flete AS FLOAT) + CAST(impe.total_seguros AS FLOAT) + CAST(impe.total_embalages AS FLOAT) +
                    CAST(impe.total_otros_inc AS FLOAT) + CAST(impe.total_otros_ded AS FLOAT)) AS valor_aduana_mxn_ped
            FROM l10n_mx_immex_pedimento AS  impe
            LEFT JOIN (SELECT pedimento_id,
                SUM(CASE WHEN clave_contribucion = '1' THEN CAST(importe AS FLOAT) ELSE 0.0 END) AS DTA,
                SUM(CASE WHEN clave_contribucion = '15' THEN CAST(importe AS FLOAT) ELSE 0.0 END) AS PREVIO
                FROM l10n_mx_immex_pedimento_contribuciones GROUP BY pedimento_id) AS ped_cont ON impe.id = ped_cont.pedimento_id

            LEFT JOIN l10n_mx_immex_pedimento_factura AS impefac ON impe.id = impefac.pedimento_id
            LEFT JOIN (SELECT pedimento_id, SUM(CAST(monto_usd AS FLOAT)) AS sum_usd FROM l10n_mx_immex_pedimento_factura GROUP BY pedimento_id)
                AS sum_impefac ON impe.id = sum_impefac.pedimento_id
            LEFT JOIN l10n_mx_immex_pedimento_factura_mercancia AS impefacmer ON impefac.id = impefacmer.immex_invoice_id

            LEFT JOIN l10n_mx_immex_partida AS impat ON impefacmer.partida_id = impat.id
            LEFT JOIN (SELECT partida_id,
                        SUM(CASE WHEN clave_contribucion = '3' THEN CAST(importe_pago AS FLOAT) ELSE 0.0 END) AS iva_mn,
                        SUM(CASE WHEN clave_contribucion = '6' THEN CAST(importe_pago AS FLOAT) ELSE 0.0 END) AS monto_igi
                        FROM l10n_mx_immex_partida_contribuciones GROUP BY partida_id) AS part_cont ON impat.id = part_cont.partida_id
            LEFT JOIN (SELECT partida_id,
                        STRING_AGG(DISTINCT CASE WHEN tasa_contribucion = '6' THEN tasa_contribucion ELSE '' END, ', ') AS per_igi
                        FROM l10n_mx_immex_partida_tasas GROUP BY partida_id) AS part_tasas ON impat.id = part_tasas.partida_id

            LEFT JOIN (SELECT STRING_AGG(pp.default_code, ', ') AS default_code, pt.immex_type_id
                FROM product_template AS pt
                JOIN product_product AS pp ON pt.id = pp.product_tmpl_id
                WHERE pp.active IS TRUE AND pt.immex_type_id IS NOT NULL
                GROUP BY pt.immex_type_id) AS pp ON impat.immex_type_id = pp.immex_type_id
            WHERE impe.tipo_operacion = '1'
                AND impe.clave_documento IN ('IN', 'V1', 'AF', 'RT')
                AND '%s' <= impe.fecha_pedimento  AT TIME ZONE 'UTC' AT TIME ZONE 'America/Mexico_City'
                AND CAST('%s' AS DATE) + INTERVAL '1' DAY > impe.fecha_pedimento AT TIME ZONE 'UTC' AT TIME ZONE 'America/Mexico_City'
            ORDER BY impe.pedimento_num, impat.id, impefac.id, impefacmer.id
        """ % (objects.fecha_inicio.strftime('%Y-%m-%d'), objects.fecha_final.strftime('%Y-%m-%d')))
        return self._cr.fetchall()
