# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from lxml import etree, objectify
import base64


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    authorized = fields.Boolean(
        string='Autorizar',
    )

    @api.multi
    def button_stock_picking(self):
        self.authorized = True

    @api.multi
    def button_validate(self):
        for stock in self:
            origin = stock.location_id.usage
            destin = stock.location_dest_id.usage
            if origin == 'inventory' or destin == 'inventory':
                if not self.authorized:
                    raise UserError(_("No se ha solicitado la autorización de este movimiento"))
                if not self.env.user.has_group(
                        'stock_picking_validate.group_button_validate_adjustment'):
                    raise UserError(
                        _('Error!\nDoes not count on provilegios to validate this exit by adjustment.'))
            product_ids = stock.move_line_ids_without_package.mapped(
                'product_id')
            for product in product_ids:
                qty_done = sum(stock.move_line_ids_without_package.filtered(
                    lambda sml: sml.product_id.id == product.id).mapped(
                    'qty_done'))
                qty = sum(stock.move_ids_without_package.filtered(
                    lambda sm: sm.product_id.id == product.id).mapped(
                    'product_uom_qty'))
                if round(qty_done, 6) > round(qty, 6):
                    raise UserError((
                        'Error!\nEsta queriendo traspasar una cantidad %s mayor a la disponible %s') % (round(qty_done, 6), round(qty, 6)))
            # for line in stock.move_line_ids_without_package:
            #     if line.product_uom_qty < line.qty_done:
            #         raise UserError(
            #             'Error!\nEsta queriendo traspasar una cantidad mayor a la disponible')

        return super().button_validate()

    @api.multi
    def set_quantities_from_xml(self):
        for rec in self:
            xml_attachment = self.env['ir.attachment'].search(
                [('res_model', '=', 'stock.picking'),
                 ('res_id', '=', rec.id)]).filtered(
                lambda att: att.name[-4:].upper() == '.XML')

            if not xml_attachment:
                raise UserError(("No XML file found"))

            if len(xml_attachment) > 1:
                raise UserError(("More than 1 XML found"))

            xml_cfdi = objectify.fromstring(base64.decodestring(xml_attachment.datas))

            ns_map = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}

            conceptos = xml_cfdi.find('cfdi:Conceptos', namespaces=ns_map)

            # Apply the same logic to the above example data
            aggregate_concepts = {}
            for concepto in conceptos.iterchildren():
                no_identificacion = concepto.get('NoIdentificacion')
                cantidad = float(concepto.get('Cantidad'))

                if no_identificacion not in aggregate_concepts:
                    aggregate_concepts[no_identificacion] = 0
                aggregate_concepts[no_identificacion] += cantidad

            consolidado = tuple(
                {'NoIdentificacion': key, 'Cantidad': value} for key, value in aggregate_concepts.items()
            )

            for elemento in consolidado:
                product = self.env['product.product'].search([
                    ('default_code', '=', elemento['NoIdentificacion'])
                ])
                if not product:
                    product = self.env['product.product'].with_context(
                        active_test=False).search([
                            ('default_code', '=', elemento['NoIdentificacion'])
                        ])

                moves = self.env['stock.move'].search([
                    ('picking_id', '=', rec.id),
                    ('product_id', '=', product.id),
                    ('product_uom_qty', '>', 0),
                    ('state', 'not in', ('cancel', 'done'))
                ])

                remaining = float(elemento['Cantidad'])

                for mov in moves:
                    if mov.product_uom_qty < remaining:
                        mov.write({'quantity_done': mov.product_uom_qty})
                        remaining = remaining - mov.product_uom_qty
                    else:
                        mov.write({'quantity_done': remaining})
                        remaining = remaining - remaining

                product_info = str(product.default_code) + ' - ' + str(product.product_tmpl_id.name) + ' o ' + elemento['NoIdentificacion']

                if remaining > 0.00:
                    raise UserError(
                        _("There is a remaining quantity %s of this product %s probably you uploaded a wrong XML file") % (remaining, product_info))
