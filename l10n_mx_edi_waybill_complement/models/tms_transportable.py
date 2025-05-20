# -*- coding: utf-8 -*-

from odoo import api, models, fields


class TmsTransportable(models.Model):
    _inherit = 'tms.transportable'

    dangerous = fields.Boolean(
        string='Dangerous',
    )

    packing_type_id = fields.Many2one(
        'l10n.mx.wbl.packing.type',
        string='Packing Type',
    )

    products_services_id = fields.Many2one(
        'l10n.mx.wbl.products.services',
        string='Code Products Services',
    )

    threatening = fields.Selection(
        related='products_services_id.threatening',
        store=True,
        readonly=True,
        string='Dangerous'
    )

    dangerous_material_id = fields.Many2one(
        'l10n.mx.wbl.dangerous.material',
        string='Dangerous Material',
    )

    l10n_mx_edi_tariff_fraction_id = fields.Many2one(
        'l10n_mx_edi.tariff.fraction', 'Tariff Fraction',
        help='It is used to express the key of the tariff fraction '
        'corresponding to the description of the product to export. Node '
        '"FraccionArancelaria" to the concept.')

    @api.onchange('products_services_id')
    def onchange_products_services_id(self):
        if self.products_services_id.dangerous:
            self.dangerous = True
        else:
            self.dangerous = False
            self.dangerous_material_id = False
            self.packing_type_id = False
