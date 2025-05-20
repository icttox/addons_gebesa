# -*- coding: utf-8 -*-
# © 2022 Samuel Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.management_system_gebesa.daily_inspection_report'
    _description = 'Report Daily Inspection'

    @api.model
    def get_flaw(self, workcenter):
        return self.env['quality.alert.flaw'].search(
            [('workcenter_ids', 'in' [workcenter])])

    @api.multi
    def _get_report_values(self, docids, data=None):

        alerts = self.env['quality.alert'].browse(docids)
        alert_ids = {}
        workcenter_ids = {}

        for date in alerts.mapped('date'):
            alert_ids[date] = {}
            alert_date = alerts.filtered(
                lambda aler: aler.date == date)

            for workcenter in alert_date.mapped('workcenter_id'):
                alert_ids[date][workcenter.id] = {}
                workcenter_ids[workcenter.id] = workcenter
                alert_center = alert_date.filtered(
                    lambda aler: aler.workcenter_id.id == workcenter.id)

                for oven in alert_center.mapped('oven'):
                    alert_ids[date][workcenter.id][oven] = {}
                    alert_oven = alert_center.filtered(
                        lambda aler: aler.oven == oven)

                    for sale in alert_oven.mapped('sale_id'):
                        alert_ids[date][workcenter.id][oven][sale.id] = {}
                        alert_sale = alert_oven.filtered(
                            lambda aler: aler.sale_id.id == sale.id)
                        for prod in alert_sale.mapped('product_id'):
                            alert_ids[date][workcenter.id][oven][sale.id][prod.id] = alert_sale.filtered(
                                lambda aler: aler.product_id.id == prod.id)
                    alert_sale = alert_oven.filtered(
                        lambda aler: not aler.sale_id.id)
                    if alert_sale:
                        alert_ids[date][workcenter.id][oven][0] = {}
                        for prod in alert_sale.mapped('product_id'):
                            alert_ids[date][workcenter.id][oven][0][prod.id] = alert_sale.filtered(
                                lambda aler: aler.product_id.id == prod.id)

        docargs = {
            'doc_ids': docids,
            'doc_model': 'quality.alert',
            'docs': alerts,
            'data': data,
            'alert_ids': alert_ids,
            'workcenter_ids': workcenter_ids,
            'get_flaw': self.get_flaw
        }
        return docargs
