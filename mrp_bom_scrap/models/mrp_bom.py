# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class MrpBom(models.Model):
    _name = "mrp.bom"
    _inherit = "mrp.bom"

    scrap_ids = fields.One2many(
        'mrp.bom.scrap',
        'bom_id',
        string='Scrap',
        compute='_compute_kilos_bom',
        store=True,
    )

    @api.depends('bom_line_ids.bom_line_detail_ids',
                 'bom_line_ids.product_qty',
                 'bom_line_ids.bom_line_detail_ids.kilos',
                 'bom_line_ids.bom_line_detail_ids.meters2',
                 'bom_line_ids.bom_line_detail_ids.quantity',
                 'bom_line_ids.bom_line_detail_ids.caliber_id')
    def _compute_kilos_bom(self):
        for bom in self:
            calibers = {}
            line_calibers = {}
            details = bom.mapped('bom_line_ids').mapped(
                'bom_line_detail_ids').filtered(
                lambda det: det.caliber_id)
            for det in details:
                line_id = det.bom_line_id
                caliber_id = det.caliber_id
                if line_id.id not in line_calibers.keys():
                    line_calibers[line_id.id] = {}
                if caliber_id not in line_calibers[line_id.id].keys():
                    line_calibers[line_id.id][caliber_id] = {}
                    line_calibers[line_id.id][caliber_id]['meters'] = 0
                    line_calibers[line_id.id][caliber_id]['qty'] = (
                        line_id.product_qty)
                    line_calibers[line_id.id][caliber_id]['scrap'] = 0
                    line_calibers[line_id.id][caliber_id]['kilo'] = 0
                met = det.quantity * det.meters2
                kil = det.quantity * det.kilos
                line_calibers[line_id.id][caliber_id]['meters'] += met
                line_calibers[line_id.id][caliber_id]['kilo'] += kil
            for line in line_calibers:
                for caliber in line_calibers[line].keys():
                    if caliber not in calibers.keys():
                        calibers[caliber] = {}
                        calibers[caliber]['kilo'] = 0
                        calibers[caliber]['meters'] = 0
                        calibers[caliber]['scrap'] = 0
                    scrap = (((line_calibers[line][caliber]['qty'] -
                               line_calibers[line][caliber]['kilo']) * 100) /
                             line_calibers[line][caliber]['qty'])
                    calibers[caliber]['kilo'] += line_calibers[line][caliber][
                        'kilo']
                    calibers[caliber]['meters'] += line_calibers[line][
                        caliber]['meters']
                    calibers[caliber]['scrap'] += scrap

            new_lines = self.env['mrp.bom.scrap']
            for key in calibers:
                data = {
                    'kilos': calibers[key]['kilo'],
                    'metros': calibers[key]['meters'],
                    'caliber_id': key,
                    'scrap': calibers[key]['scrap'],
                }
                new_line = new_lines.new(data)
                new_lines += new_line
            bom.scrap_ids += new_lines

        return {}
