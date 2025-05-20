# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    travel_id = fields.Many2one(
        'tms.travel',
        string='Travel',
    )
    shipment_id = fields.Many2one(
        'mrp.shipment',
        string='Embarque',
    )

    travel_ids = fields.One2many(
        'tms.travel', 'invoice_id', string="Travel", readonly=True)

    @api.one
    @api.constrains('company_id', 'account_analytic_id', 'type','travel_id')
    def _unique_travel(self):
        if self.type != 'in_invoice' or not self.travel_id:
            return
        invoice = self.env['account.invoice'].search(
            [('company_id', '=', self.company_id.id),
             ('account_analytic_id', '=', self.account_analytic_id.id),
             ('type', '=', self.type),
             ('travel_id', '=', self.travel_id.id),
             ('state', '!=', 'cancel'),
             ('id', '!=', self.id)]) or False
        if invoice:
            raise ValidationError(_("Error. Duplicate Travel."))

    @api.one
    @api.constrains('company_id', 'account_analytic_id', 'type', 'shipment_id')
    def _unique_shipment(self):
        if self.type != 'in_invoice' or not self.shipment_id:
            return
        invoicea = self.env['account.invoice'].search(
            [('company_id', '=', self.company_id.id),
             ('account_analytic_id', '=', self.account_analytic_id.id),
             ('type', '=', self.type),
             ('shipment_id', '=', self.shipment_id.id),
             ('state', '!=', 'cancel'),
             ('id', '!=', self.id)]) or False
        if invoicea:
            raise ValidationError(_("Error. Duplicate Shipment."))

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('move_name', operator, name),
                      ('number', operator, name)]
        invoices = self.search(domain + args, limit=limit)
        return invoices.name_get()

    @api.multi
    @api.depends('move_name', 'number')
    def name_get(self):
        res = []
        for inv in self:
            if inv.move_name and inv.number:
                res.append((inv.id, "%s %s %s" % (
                    inv.number, inv.move_name, inv.name or '')))
            elif inv.move_name and not inv.number:
                res.append((inv.id, "%s %s" % (
                    inv.move_name, inv.name or '')))
            else:
                return super().name_get()
        return res

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            if invoice.waybill_ids:
                if round(invoice.amount_total, 2) < round(sum(invoice.mapped(
                        'waybill_ids').mapped('amount_total')), 2):
                    raise ValidationError(_('The total of the invoice is less \
                        than the waybill'))
            if not invoice.travel_ids and any(line.product_id.require_travel for line in invoice.invoice_line_ids):
                if not self.env.user.has_group('flete_gebesa.group_invoice_without_travel'):
                    raise ValidationError(_('You do not have privileges to validate this invoice without travel.'))
        return super().invoice_validate()

    @api.multi
    def print_travel_instruction(self):
        travel_ids = self.mapped('travel_id').mapped('id')
        travels = self.env['tms.travel'].sudo().browse(travel_ids)
        if travels:
            return self.env.ref(
                'flete_gebesa.travel_instructions_2').report_action(travels)
        return
