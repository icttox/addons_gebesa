# -*- coding: utf-8 -*-
# © 2018 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import math
from odoo import api, models, _
from odoo.exceptions import ValidationError


class ParticularReport(models.AbstractModel):
    _name = 'report.packing_gebesa.report_shipping_label'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.shipment'
        packing_obj = self.env['product.packing.list']
        product_obj = self.env['product.product']
        bom_obj = self.env['mrp.bom']
        shipment_ids = self.env[self.model].browse(docids)
        docs = {}
        for shipment in shipment_ids:
            docs[shipment.id] = []
            total_pages = 0
            num_page = 0
            for line in shipment.line_ids:
                product = line.product_id
                if line.packing_id:
                    if line.packing_id.qty > 0:
                        total_qty = line.quantity_shipped
                        tagged_qty = line.packing_id.qty
                        total_page = math.ceil(total_qty / tagged_qty)
                        total_pages += total_page
                        while total_qty > 0:
                            num_page += 1
                            if total_qty > tagged_qty:
                                qty = tagged_qty
                            else:
                                qty = int(total_qty)
                            docs[shipment.id].append({
                                'linea': line,
                                'numero_etiqueta': num_page,
                                'cantidad': qty,
                                'description': '',
                                'product': product
                            })
                            total_qty = total_qty - qty
                    elif line.packing_id.packing_line_ids:
                        packing_line = []
                        total_page = 0
                        for packig_line in line.packing_id.packing_line_ids:
                            total_qty = line.quantity_shipped
                            tagged_qty = packig_line.quantity
                            total_page += math.ceil(total_qty / tagged_qty)
                            while total_qty > 0:
                                num_page += 1
                                if total_qty > tagged_qty:
                                    qty = tagged_qty
                                else:
                                    qty = int(total_qty)
                                packing_line.append({
                                    'linea': line,
                                    'numero_etiqueta': num_page,
                                    'cantidad': qty,
                                    'description': packig_line.description,
                                    'product': product
                                })
                                total_qty = total_qty - qty
                        total_pages += total_page
                        docs[shipment.id].extend(packing_line)
                    else:
                        raise ValidationError(_(
                            'The %s packaging has no quantity or lines \
                            of detail.') % line.product_tmpl_id.name)
                else:
                    bom = bom_obj.search([
                        ('product_id', '=', product.id),
                        ('active', '=', True)])
                    if bom.type == 'phantom':
                        self._cr.execute(
                            """
                            WITH RECURSIVE componentes(
                                product_id, code, qty, not_kit, r) AS (
                                SELECT
                                    pp.id,
                                    pp.default_code,
                                    ROUND((
                                        mbl.product_qty / mb.product_qty) * 1,6
                                        ) AS product_qty,
                                    CASE WHEN mb2.type = 'phantom'
                                        THEN FALSE ELSE TRUE END AS not_kit,
                                    CAST(ROW_NUMBER () OVER () AS TEXT)
                                FROM mrp_bom AS mb
                                JOIN mrp_bom_line AS mbl ON mb.id = mbl.bom_id
                                JOIN product_product AS pp
                                    ON mbl.product_id = pp.id
                                LEFT JOIN mrp_bom AS mb2
                                    ON pp.id = mb2.product_id
                                WHERE mb.product_id = %s
                                    AND mb.type = 'phantom'
                                UNION SELECT
                                    pp.id,
                                    pp.default_code,
                                    ROUND(c.qty * ((
                                        mbl.product_qty / mb.product_qty) * 1),
                                         6) AS product_qty,
                                    CASE WHEN mb2.type = 'phantom'
                                        THEN FALSE ELSE TRUE END AS not_kit,
                                    CONCAT(c.r, '-', CAST(
                                        ROW_NUMBER () OVER () AS TEXT))
                                FROM componentes AS c
                                LEFT JOIN mrp_bom AS mb
                                    ON c.product_id = mb.product_id
                                JOIN mrp_bom_line AS mbl ON mb.id = mbl.bom_id
                                JOIN product_product AS pp
                                    ON mbl.product_id = pp.id
                                JOIN mrp_bom AS mb2 ON pp.id = mb2.product_id
                                WHERE c.not_kit IS false
                            )
                            SELECT product_id, code, SUM(qty) FROM componentes
                            WHERE not_kit GROUP BY product_id, code
                            ORDER BY code, product_id""",
                            ([product.id]))
                        if self._cr.rowcount:
                            for row in self._cr.fetchall():
                                product_det = product_obj.browse([row[0]])
                                packing = packing_obj.search([
                                    ('product_tmpl_id', '=',
                                     product_det.product_tmpl_id.id),
                                    ('active', '=', True),
                                    ('type', '=', 'standard')
                                ])
                                if not packing:
                                    raise ValidationError(_(
                                        'The product %s must have captured a packaging.')
                                        % product_det.product_tmpl_id.name)
                                if packing.qty > 0:
                                    total_qty = line.quantity_shipped * row[2]
                                    tagged_qty = packing.qty
                                    total_page = math.ceil(
                                        total_qty / tagged_qty)
                                    total_pages += total_page
                                    while total_qty > 0:
                                        num_page += 1
                                        if total_qty > tagged_qty:
                                            qty = tagged_qty
                                        else:
                                            qty = int(total_qty)
                                        docs[shipment.id].append({
                                            'linea': line,
                                            'numero_etiqueta': num_page,
                                            'cantidad': qty,
                                            'description': '',
                                            'product': product_det
                                        })
                                        total_qty = total_qty - qty
                                elif packing.packing_line_ids:
                                    packing_line = []
                                    total_page = 0
                                    for packig_line in packing.packing_line_ids:
                                        total_qty = (
                                            line.quantity_shipped * row[2])
                                        tagged_qty = packig_line.quantity
                                        total_page += math.ceil(
                                            total_qty / tagged_qty)
                                        while total_qty > 0:
                                            num_page += 1
                                            if total_qty > tagged_qty:
                                                qty = tagged_qty
                                            else:
                                                qty = int(total_qty)
                                            packing_line.append({
                                                'linea': line,
                                                'numero_etiqueta': num_page,
                                                'cantidad': qty,
                                                'description': packig_line.description,
                                                'product': product_det
                                            })
                                            total_qty = total_qty - qty
                                    total_pages += total_page
                                    docs[shipment.id].extend(packing_line)
                                else:
                                    raise ValidationError(_(
                                        'The %s packaging has no quantity or lines \
                                        of detail.')
                                        % product_det.product_tmpl_id.name)
                    else:
                        raise ValidationError(
                            _('The product %s must have captured a packaging.')
                            % line.product_tmpl_id.name)

            for page in docs[shipment.id]:
                page['total'] = total_pages
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': docs,
        }
        return docargs
