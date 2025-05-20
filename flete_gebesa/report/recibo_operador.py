# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.flete_gebesa.report_recibo_operador'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'tms.expense'
        # report_obj = self.env['report']
        # report = report_obj._get_report_from_name(
        # 'flete_gebesa.report_recibo_operador')
        expense_obj = self.env['tms.expense']
        expenses = expense_obj.browse(docids)
        exp = {}

        for expense in expenses:
            exp[expense.id] = {}
            exp[expense.id]['viajes'] = ''
            exp[expense.id]['rutas'] = ''
            exp[expense.id]['cajas'] = ''
            exp[expense.id]['cartas'] = ''
            exp[expense.id]['clientes'] = ''
            exp[expense.id]['peso'] = 0
            exp[expense.id]['invoice_id'] = ''
            exp[expense.id]['attachment_count'] = 0
            exp[expense.id]['total_cartas'] = 0
            exp[expense.id]['total_gasolina'] = 0
            exp[expense.id]['total_salario'] = 0
            exp[expense.id]['total_gastos'] = 0
            exp[expense.id]['total_casetas'] = 0
            for travel in expense.travel_ids:
                if travel.state != 'cancel':
                    exp[expense.id]['viajes'] += travel.name + ','
                    ruta_viaje = ''
                    if travel.route_id.name:
                        ruta_viaje += travel.route_id.name
                    else:
                        ruta_viaje = 'Sin Ruta Definida'
                    exp[expense.id]['rutas'] = ruta_viaje
                    exp[expense.id]['cajas'] += travel.trailer1_id.name + ','
                    exp[expense.id]['clientes'] += travel.partner_id.name + ','
                    exp[expense.id]['total_cartas'] += travel.amount_untaxed
                    exp[expense.id]['attachment_count'] += travel.attachment_count
                    factura_viaje = ''
                    if travel.invoice_id and travel.invoice_id.number:
                        factura_viaje = travel.invoice_id.number
                    elif travel.invoice_id and travel.invoice_id.move_name:
                        factura_viaje = travel.invoice_id.move_name + ' Cancelada'
                    else:
                        factura_viaje = 'No contiene Factura'
                    exp[expense.id]['invoice_id'] = factura_viaje
                for line in travel.transportable_line_ids:
                    exp[expense.id]['peso'] += line.quantity
                for stop in travel.travel_stop_ids:
                    exp[expense.id]['direccion'] = stop.address
                    exp[expense.id]['latitud'] = stop.latitude
                    exp[expense.id]['longitud'] = stop.longitude
                    exp[expense.id]['distancia'] = stop.distance
                    exp[expense.id]['duracion'] = stop.duration
                    exp[expense.id]['from_date'] = stop.from_date
                    exp[expense.id]['to_date'] = stop.to_date
                for coast in travel.gear_coast_ids:
                    exp[expense.id]['from_date'] = coast.begin_date_time
                    exp[expense.id]['initial_speed'] = coast.begin_speed
                    exp[expense.id]['begin_latitude'] = coast.begin_latitude
                    exp[expense.id]['begin_longitud'] = coast.begin_longitude
                    exp[expense.id]['from_date_end'] = coast.end_date_time
                    exp[expense.id]['final_speed'] = coast.end_speed
                    exp[expense.id]['end_latitude'] = coast.end_latitude
                    exp[expense.id]['end_longitude'] = coast.end_longitude
                    exp[expense.id]['distance'] = coast.distance
                    exp[expense.id]['duration'] = coast.duration
                    exp[expense.id]['max_speed'] = coast.max_speed
                    exp[expense.id]['avg_speed'] = coast.avg_speed
            for line in expense.expense_line_ids:
                if line.product_id.tms_product_category == 'fuel':
                    exp[expense.id]['total_gasolina'] -= line.price_total
                elif line.product_id.tms_product_category == 'salary':
                    exp[expense.id]['total_salario'] += line.price_total
                else:
                    exp[expense.id]['total_gastos'] -= line.price_total
            for tollstation in expense.tollstation_ids:
                exp[expense.id]['total_casetas'] -= tollstation.amount

            tot_gasto = (
                exp[expense.id]['total_gasolina'] +
                (exp[expense.id]['total_salario'] * -1) +
                exp[expense.id]['total_casetas'] +
                exp[expense.id]['total_gastos'])
            exp[expense.id]['utilidad'] = (exp[expense.id]['total_cartas'] +
                                           tot_gasto)
            if exp[expense.id]['total_cartas'] > 0:
                exp[expense.id]['margen'] = (exp[expense.id]['utilidad'] / exp[expense.id]['total_cartas']) * 100
            else:
                exp[expense.id]['margen'] = 0
        docargs = {
            'doc_ids': docids,
            # 'doc_model': report.model,
            'doc_model': self.model,
            'docs': expenses,
            'expenses': exp
        }
        # return report_obj.render(
        # 'flete_gebesa.report_recibo_operador', docargs)
        return docargs
