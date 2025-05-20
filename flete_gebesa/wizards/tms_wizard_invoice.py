# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, exceptions, models, _


class TmsWizardInvoice(models.TransientModel):
    _inherit = 'tms.wizard.invoice'

    @api.model
    def compute_waybill(self, record, lines):
        res = super().compute_waybill(record, lines)
        for line in res['lines']:
            line[2]['price_unit'] = line[2]['price_unit'] / line[2]['quantity']
            if 'account_analytic_id' not in line[2].keys():
                line[2]['account_analytic_id'] = (
                    record.travel_ids.unit_id.account_analytic_id.id)
        return res

    @api.model
    def compute_fuel_log(self, record, lines):
        res = super().compute_fuel_log(record, lines)
        for line in res['lines']:
            if 'account_analytic_id' not in line[2].keys():
                line[2]['account_analytic_id'] = (
                    record.travel_id.unit_id.account_analytic_id.id)
        return res

    @api.model
    def compute_tollstation(self, record, lines):
        res = {}
        res['invoice_type'] = 'in_invoice'
        res['operating_unit_id'] = record.operating_unit_id
        partner_id = False
        if len(record.product_id.seller_ids) != 0:
            partner_id = record.product_id.seller_ids[0].name
        if not partner_id:
            raise exceptions.ValidationError(
                _('This product does not have a supplier'))
        res['partner_id'] = partner_id
        fpos = partner_id.property_account_position_id
        res['fpos'] = fpos
        res['invoice_account'] = fpos.map_account(
            partner_id.property_account_payable_id)
        product = record.product_id
        if product.property_account_expense_id:
            account = product.property_account_expense_id
        elif product.categ_id.property_account_expense_categ_id:
            account = (
                product.categ_id.property_account_expense_categ_id)
        else:
            raise exceptions.ValidationError(
                _('You must have an expense account in the '
                  'product or its category'))
        tax = fpos.map_tax(product.supplier_taxes_id)
        lines.append(
            (0, 0, self.prepare_lines
                (product, 1, record.amount, tax, account)))
        for line in lines:
            if 'account_analytic_id' not in line[2].keys():
                line[2]['name'] += (' ' + record.name + ' - ' +
                                    str(record.travel_id.name))
                line[2]['account_analytic_id'] = (
                    record.unit_id.account_analytic_id.id)
        res['lines'] = lines
        return res

    @api.multi
    def make_invoices(self):
        record_names = []
        currency_ids = []
        partner_ids = []
        lines = []
        active_model = self._context.get('active_model')
        records = self.env[active_model].browse(
            self._context.get('active_ids'))
        acc_ana_id = False
        journal_id = False
        for record in records:
            if record.invoice_id:
                raise exceptions.ValidationError(
                    _('The record is already invoiced'))
            if record.state not in ['confirmed', 'closed']:
                raise exceptions.ValidationError(
                    _('The record must be confirmed or closed'))
            record_names.append(record.name)
            currency_ids.append(record.currency_id.id)
            currency_id = record.currency_id.id
            # journal_id = record.operating_unit_id.sale_journal_id.id
            if active_model == 'tms.waybill':
                res = self.compute_waybill(record, lines)
                acc_ana_id = (
                    record.operating_unit_id.analytic_account_id.id)
                journal_id = (
                    record.operating_unit_id.sale_journal_id.id)
            elif active_model == 'fleet.vehicle.log.fuel':
                res = self.compute_fuel_log(record, lines)
                acc_ana_id = (
                    record.operating_unit_id.analytic_account_id.id)
                journal_id = (
                    record.operating_unit_id.purchase_journal_id.id)
            elif active_model == 'tms.travel.tollstation':
                res = self.compute_tollstation(record, lines)
                acc_ana_id = (
                    record.operating_unit_id.analytic_account_id.id)
                journal_id = (
                    record.operating_unit_id.purchase_journal_id.id)
            partner_ids.append(res['partner_id'].id)
        if len(set(partner_ids)) > 1:
            raise exceptions.ValidationError(
                _('The records must be of the same partner.'))
        if len(set(currency_ids)) > 1:
            raise exceptions.ValidationError(
                _('The records must be of the same currency.'))
        invoice_id = self.env['account.invoice'].create({
            'partner_id': res['partner_id'].id,
            'operating_unit_id': res['operating_unit_id'].id,
            'fiscal_position_id': res['fpos'].id,
            'journal_id': journal_id,
            'currency_id': currency_id,
            'account_id': res['invoice_account'].id,
            'type': res['invoice_type'],
            'invoice_line_ids': [line for line in res['lines']],
            'account_analytic_id': acc_ana_id,
            'company_id': res['operating_unit_id'].company_id.id,
        })
        for record in records:
            record.write({'invoice_id': invoice_id.id})
        message = _(
            '<strong>Invoice of:</strong> %s </br>') % (
            ', '.join(record_names))
        invoice_id.message_post(body=message)

        return {
            'name': 'Customer Invoice',
            'view_id': self.env.ref(
                'account.invoice_supplier_form').id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'res_model': 'account.invoice',
            'res_id': invoice_id.id,
            'type': 'ir.actions.act_window'
        }
