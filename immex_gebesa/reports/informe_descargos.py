# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class InputReport(models.AbstractModel):
    _name = 'report.immex_gebesa.report_informe_descargos'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'informe.descargos.wizard'
        descargos_obj = self.env[self.model]
        descargos = descargos_obj.browse(docids)

        fracciones = []
        detalles = []
        for desc in descargos:
            self._cr.execute("""
                SELECT
                    ped.clave_aduana,
                    ped.patente,
                    ped.num_pedimento
                FROM l10n_mx_immex_pedimento AS ped
                WHERE ped.clave_documento = '%s'
                    AND EXTRACT(MONTH FROM CAST(ped.fecha_pago_real AS date)) = %s
                    AND EXTRACT(YEAR FROM CAST(ped.fecha_pago_real AS date)) = %s
                ORDER BY ped.clave_aduana,ped.patente,ped.num_pedimento
            """ % (desc.tipo_descargo, desc.periodo, desc.year))
            for det in self._cr.fetchall():
                detalles.append(det)

            self._cr.execute("""
                SELECT
                    par.fraccion_arancelaria,
                    ROUND(CAST(SUM(CAST(par.valor_usd AS FLOAT)/CAST(par.cantidad_udm_comercial AS FLOAT)*CAST(ped_id.tipo_cambio AS FLOAT)*des_lin.quantity) AS NUMERIC),2) AS total
                FROM l10n_mx_immex_pedimento AS ped
                JOIN l10n_mx_immex_pedimento_factura AS fac ON ped.id = fac.pedimento_id
                JOIN account_invoice AS ai ON fac.invoice_id = ai.id
                JOIN account_invoice_line AS ail ON ai.id = ail.invoice_id
                JOIN l10n_mx_immex_partida_descargue AS des ON ail.id = des.invoice_line_id
                JOIN l10n_mx_immex_partida_descargue_line AS des_lin ON des.id = des_lin.descargue_id
                JOIN l10n_mx_immex_partida AS par ON des_lin.partida_id = par.id
                JOIN l10n_mx_immex_pedimento AS ped_id ON par.pedimento_id = ped_id.id
                WHERE ped.clave_documento = '%s'
                    AND EXTRACT(MONTH FROM CAST(ped.fecha_pago_real AS date)) = %s
                    AND EXTRACT(YEAR FROM CAST(ped.fecha_pago_real AS date)) = %s
                GROUP BY par.fraccion_arancelaria
                ORDER BY par.fraccion_arancelaria
            """ % (desc.tipo_descargo, desc.periodo, desc.year))
            for fra in self._cr.fetchall():
                fracciones.append(fra)

            # start_date = datetime.datetime(int(desc.year), int(desc.periodo), 1)
            # end_date = start_date + relativedelta(months=1)

        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': descargos,
            'data': data,
            'fracciones': fracciones,
            'detalles': detalles
        }
        return docargs
