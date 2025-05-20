# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
# from ast import literal_eval
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def recalculating_sales_data(self):
        product_obj = self.env['product.product']
        deposit_product_id = self.env[
            'ir.config_parameter'].sudo().get_param(
                'sale.default_deposit_product_id')

        for inv in self:
            global_cost = 0.0
            global_net_sale = 0.0
            global_freight = 0.0
            global_installa = 0.0
            global_profit_margin = 0.0
            for line in inv.invoice_line_ids:
                if line.product_id and not line.product_id.landed_cost_ok:
                    if deposit_product_id == line.product_id.id:
                        net_sale = line.price_subtotal
                        freight = 0.0
                        installation = 0.0
                        profit_margin = 0.0
                        standard_cost = 0.0
                        total_cost = 0.0
                    else:
                        product = product_obj.browse(line.product_id.id)
                        standard_cost = product.standard_price or 0.0
                        if standard_cost > 0:
                            standard_cost = standard_cost * inv.rate
                        total_cost = standard_cost * line.quantity

                        perc_freight = inv.perc_freight or False
                        freight = 0.0
                        profit_margin = 0.0
                        perc_installation = inv.perc_installation or False
                        installation = 0.0

                        net_sale = (1 - (line.discount / 100)) * (
                            line.price_unit * line.quantity)
                        tax_ids = line.invoice_line_tax_ids.filtered(
                            lambda tax: tax.price_include)
                        for tax in tax_ids:
                            if tax.amount_type == 'percent':
                                net_sale = net_sale / (1 + tax.amount / 100)
                            elif tax.amount_type == 'division':
                                net_sale = net_sale - (
                                    net_sale * tax.amount / 100)
                        if perc_freight:
                            freight = net_sale * (perc_freight / 100.0)
                        net_sale = net_sale - freight
                        if perc_installation:
                            installation = net_sale * (
                                perc_installation / 100.0)
                        net_sale = net_sale - installation

                        if net_sale > 0.000000:
                            profit_margin = (1 - (total_cost) / net_sale)
                            profit_margin = profit_margin * 100

                    line.freight_amount = freight
                    line.installation_amount = installation
                    line.net_sale = net_sale
                    line.profit_margin = profit_margin
                    line.standard_cost = standard_cost
                    line.total_cost = total_cost

                    global_cost += total_cost
                    global_net_sale += net_sale
                    global_freight += freight
                    global_installa += installation
            if global_net_sale > 0.000000:
                global_profit_margin = (1 - (global_cost) / global_net_sale)
                global_profit_margin = global_profit_margin * 100

            inv.total_cost = global_cost
            inv.total_net_sale = global_net_sale
            inv.total_freight = global_freight
            inv.total_installation = global_installa
            inv.profit_margin = global_profit_margin

        return True

    @api.model
    def invoice_line_move_line_get(self):
        deposit_product_id = self.env[
            'ir.config_parameter'].sudo().get_param(
                'sale.default_deposit_product_id')
        res = []
        if self.type in ['in_invoice', 'in_refund']:
            return super().invoice_line_move_line_get()

        # freight_account_id = literal_eval(self.env[
        #     'ir.config_parameter'].sudo().get_param(
        #         'res_settings_freight.freight_account_id', 'False'))
        # installation_account_id = literal_eval(self.env[
        #     'ir.config_parameter'].sudo().get_param(
        #         'res_settings_freight.installation_account_id', 'False'))
        freight_account_id = self.company_id.freight_account_id.id
        installation_account_id = self.company_id.installation_account_id.id

        if not freight_account_id and self.company_id.is_manufacturer:
            raise ValidationError(_(u"Please specify an account of \
                                  freight in Accounting --> \
                                  Configuration --> Settings"))
        if not installation_account_id and self.company_id.is_manufacturer:
            raise ValidationError(_(u"Please specify an account of \
                                  installation in Accounting --> \
                                  Configuration --> Settings"))

        for line in self.invoice_line_ids:
            tax_ids = []
            for tax in line.invoice_line_tax_ids:
                tax_ids.append((4, tax.id, None))
                for child in tax.children_tax_ids:
                    if child.type_tax_use != 'none':
                        tax_ids.append((4, child.id, None))

            sale = line.price_subtotal
            total_freight = total_installation = 0.0

            analytic_id = line.account_analytic_id.id
            product_tmpl_id = line.product_id.product_tmpl_id
            if product_tmpl_id.type != 'service' and self.company_id.is_manufacturer:
                if not product_tmpl_id.family_id:
                    raise ValidationError(_(
                        "El producto %s no tiene familia asignada") %
                        line.product_id.default_code)
                if not product_tmpl_id.family_id.analytic_id:
                    raise ValidationError(_(
                        "La familia %s no tiene asignada una cuenta analitica") %
                        product_tmpl_id.family_id.name)
                analytic_id = product_tmpl_id.family_id.analytic_id.id

            if int(deposit_product_id) != line.product_id.id:
                if self.perc_freight > 0.0:
                    total_freight = sale * (self.perc_freight / 100)
                    sale = sale - total_freight
                if self.perc_installation > 0.0:
                    total_installation = sale * (self.perc_installation / 100)
                    sale = sale - total_installation

            amount = sale + total_installation + total_freight
            if (line.price_subtotal - amount) != 0:
                sale = sale + (line.price_subtotal - amount)

            move_line_dict = {
                'invl_id': line.id,
                'type': 'src',
                'name': line.name.split('\n')[0][:64],
                'price_unit': line.price_unit,
                'quantity': line.quantity,
                'price': sale,
                'account_id': line.account_id.id,
                'product_id': line.product_id.id,
                'uom_id': line.uom_id.id,
                'account_analytic_id': analytic_id,
                'tax_ids': tax_ids,
                'invoice_id': self.id,
            }
            if total_freight > 0.0:
                move_line_freight_dict = {
                    'invl_id': line.id,
                    'type': 'src',
                    'name': line.name.split('\n')[0][:64],
                    'price': total_freight,
                    'account_id': freight_account_id,
                    'product_id': False,
                    'account_analytic_id': analytic_id,
                    'tax_ids': tax_ids,
                    'invoice_id': self.id,
                }
            if total_installation > 0.0:
                move_line_installation_dict = {
                    'invl_id': line.id,
                    'type': 'src',
                    'name': line.name.split('\n')[0][:64],
                    'price': total_installation,
                    'account_id': installation_account_id,
                    'product_id': False,
                    'account_analytic_id': analytic_id,
                    'tax_ids': tax_ids,
                    'invoice_id': self.id,
                }

            # if line['account_analytic_id']:
            #     move_line_dict['analytic_line_ids'] = [(
            #         0, 0, line._get_analytic_line())]
            #     if total_freight > 0.0:
            #         move_line_freight_dict['analytic_line_ids'] = [(
            #             0, 0, line._get_analytic_line())]
            #     if total_installation > 0.0:
            #         move_line_installation_dict['analytic_line_ids'] = [(
            #             0, 0, line._get_analytic_line())]

            res.append(move_line_dict)
            if total_freight > 0.0:
                res.append(move_line_freight_dict)
            if total_installation > 0.0:
                res.append(move_line_installation_dict)
        return res

    @api.multi
    def action_move_create(self):
        res = super().action_move_create()
        for inv in self:
            inv.recalculating_sales_data()
        return res
