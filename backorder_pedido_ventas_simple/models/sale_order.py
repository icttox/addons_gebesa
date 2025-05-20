# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # week_number = fields.Integer(
    #    'Numero de la semana',
    # )
    # currency_id = fields.Many2one(
    #     'res.currency',
    #     string='Moneda',
    # )
    rate_mex = fields.Float(
        'Rate',
        digits=dp.get_precision('Product Price'),
        store=True,
        compute="compute_rate_mex",
    )
    total_rate_mex = fields.Float(
        'Total MXN',
        store=True,
        compute="compute_sale_date_mex",
    )
    freight_rate_mex = fields.Float(
        'Flete MXN',
        store=True,
        compute="compute_sale_date_mex",
    )
    installation_rate_mex = fields.Float(
        u'Instalación MXN',
        store=True,
        compute="compute_sale_date_mex",
    )
    net_sale_rate_mex = fields.Float(
        'Vta Neta MXN',
        store=True,
        compute="compute_sale_date_mex",
    )
    amount_pending_mex = fields.Float(
        'Imp X Sur MXN',
        store=True,
        compute="compute_amount_pending_mex",
    )

    @api.depends('pricelist_id.currency_id', 'date_order')
    def compute_rate_mex(self):
        for order in self:
            if order.currency_id.id != order.company_id.currency_id.id:
                self._cr.execute("""
                    SELECT rate_mex
                    FROM res_currency_rate
                    WHERE currency_id = %s
                        AND CAST(name AS DATE) = CAST(%s AT TIME ZONE 'UTC' AT TIME ZONE 'America/Mexico_City' AS DATE)
                        AND company_id = %s
                """, (order.currency_id.id,
                      order.date_order, order.company_id.id))
                if self._cr.rowcount:
                    order.rate_mex = self._cr.fetchone()[0]
                else:
                    raise ValidationError("without capturing parity captured \
                        for the day %s of the %s currency" % (
                        order.date_order, order.currency_id.name))
            else:
                order.rate_mex = 1

    @api.depends('amount_pending', 'rate_mex')
    def compute_amount_pending_mex(self):
        for sale in self:
            pending = sale.amount_pending
            if not sale.rate_mex:
                sale.amount_pending_mex = pending
            else:
                sale.amount_pending_mex = pending * sale.rate_mex

    @api.depends('amount_untaxed', 'total_freight', 'total_installation',
                 'total_net_sale', 'rate_mex')
    def compute_sale_date_mex(self):
        for order in self:
            if not order.rate_mex:
                order.total_rate_mex = order.amount_untaxed
                order.freight_rate_mex = order.total_freight
                order.installation_rate_mex = order.total_installation
                order.net_sale_rate_mex = order.total_net_sale
            else:
                order.total_rate_mex = order.rate_mex * order.amount_untaxed
                order.freight_rate_mex = order.rate_mex * order.total_freight
                order.installation_rate_mex = order.rate_mex * order.total_installation
                order.net_sale_rate_mex = order.rate_mex * order.total_net_sale

    # @api.multi
    # def extra_data(self):
    #     for sale in self:
    #         # sale.currency_id = sale.pricelist_id.currency_id.id
    #         self._cr.execute("""SELECT rate_mex From res_currency_rate
    #                         WHERE currency_id = %s
    #                         AND CAST(name AS DATE) = CAST(%s AS DATE)
    #                         AND (company_id is null
    #                             OR company_id = %s)
    #                         """, (sale.currency_id.id,
    #                               sale.date_order, sale.company_id.id))
    #         if self._cr.rowcount:
    #             sale.rate_mex = self._cr.fetchone()[0]
    #         else:
    #             sale.rate_mex = 1

    #         sale.total_rate_mex = sale.rate_mex * sale.amount_untaxed
    #         sale.freight_rate_mex = sale.rate_mex * sale.total_freight
    #         sale.installation_rate_mex = sale.rate_mex * sale.total_installation
    #         sale.net_sale_rate_mex = sale.rate_mex * sale.total_net_sale

    # @api.multi
    # def action_done(self):
    #     super(SaleOrder, self).action_done()
    #     self.extra_data()

    # @api.model
    # def create(self, vals):
    #     campo = fields.Datetime.now()
    #     if 'date_order' in vals.keys():
    #         campo = str(vals['date_order'])
    #     arreglo = campo.split(" ")
    #     arreglo2 = arreglo[0].split("/")
    #     cadena_n = ("-").join(arreglo2)
    #     week_number = int(datetime.datetime.strptime(
    #         cadena_n, '%Y-%m-%d').strftime('%W'))
    #     vals['week_number'] = week_number
    #     return super(SaleOrder, self).create(vals)

    # @api.multi
    # def write(self, values):
    #     if 'date_order' in values.keys():
    #         campo = str(values['date_order'])
    #         arreglo = campo.split(" ")
    #         arreglo2 = arreglo[0].split("/")
    #         cadena_n = ("-").join(arreglo2)
    #         week_number = int(datetime.datetime.strptime(
    #             cadena_n, '%Y-%m-%d').strftime('%W'))
    #         values['week_number'] = week_number
    #     return super(SaleOrder, self).write(values)
