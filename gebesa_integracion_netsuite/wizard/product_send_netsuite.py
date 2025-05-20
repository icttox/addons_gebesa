# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import traceback
import logging
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

from suds.client import Client

_logger = logging.getLogger()


class ProductSendNetsuite(models.TransientModel):
    _name = 'product.send.netsuite.wizard'
    _description = 'descripcion pendiente'

    nst_plant_id = fields.Many2one(
        'product.nst.plant',
        string='NetSuite Plant',
    )
    nst_line_id = fields.Many2one(
        'product.nst.line',
        string='NetSuite Line',
    )
    nst_tipo_id = fields.Many2one(
        'product.nst.tipo',
        string='NetSuite Group',
    )

    @api.multi
    def add_netsuite(self):
        product_obj = self.env['product.product']
        res_ids = self._context.get('active_ids')
        products = product_obj.browse(res_ids)
        for prod in products:
            description = ''
            concatenate = ''
            # si prod descripcion no trae nada es = 0
            description = prod.description_sale
            if not description:
                # si notrae nada asigna el valor de descripcion a name
                description = prod.name
            concatenate = prod.default_code + ';' + prod.name + ';' + \
                description + ';' + str(prod.standard_price) + \
                ';' + str(prod.id) + ';' + str(self.nst_plant_id.nstid) + \
                ';' + str(self.nst_line_id.nstid) + ';' \
                + str(self.nst_tipo_id.nstid) + '|'

            try:
                client = Client(
                    'http://148.244.148.218:8089/OdooNSProduct/Service1.asmx?wsdl'
                )

                resultado = client.service.productToItem(concatenate)

                if 'Error' in resultado:
                    raise UserError(
                        _('Failed to send NetSuite'))

                resultado = resultado.split(";")
                prod.id_ns = resultado[1]

            except Exception as e:
                error = tools.ustr(traceback.format_exc())
                _logger.error(error)
                return False
