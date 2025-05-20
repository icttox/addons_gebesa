# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

map_journal_type = {
    ('outgoing', 'customer'): ['sale'],
    ('outgoing', 'supplier'): ['purchase_refund'],
    ('outgoing', 'transit'): ['sale', 'purchase'],
    ('incoming', 'supplier'): ['purchase'],
    ('incoming', 'customer'): ['sale_refund'],
    ('incoming', 'transit'): ['purchase', 'sale'],
}


class StockInvoice(models.Model):
    _name = 'stock.invoice'
    _description = 'Stock Invoice'

    def _default_get_journal(self):
        journal_obj = self.env['account.journal']
        journal_type = self._default_get_journal_type()
        if journal_type == 'purchase_refund':
            journal_type = 'purchase'
        elif journal_type == 'sale_refund':
            journal_type = 'sale'
        journals = journal_obj.search([('type', '=', journal_type)])
        return journals and journals[0] or False

    def _default_get_journal_type(self):
        picking_obj = self.env['stock.picking']
        res_ids = self._context.get('active_ids')
        pickings = picking_obj.browse(res_ids)
        pick = pickings and pickings[0]
        if not pick or not pick.move_ids_without_package:
            return 'sale'
        type = pick.picking_type_id.code
        usage = pick.move_ids_without_package[0].location_id.usage if type == 'incoming' \
            else pick.move_ids_without_package[0].location_dest_id.usage

        return map_journal_type.get((type, usage), ['sale'])[0]

    journal_id = fields.Many2one(
        'account.journal',
        string='Destination Journal',
        default=_default_get_journal,
    )

    journal_type = fields.Selection(
        [('purchase_refund', 'Refund purchase'),
         ('purchase', 'Create supplier invoice'),
         ('sale_refund', 'Refund sale'),
         ('sale', 'Create customer invoice')],
        string="Journal type",
        default=_default_get_journal_type,
    )

    group = fields.Boolean(
        string='Group by partner',
    )

    invoice_date = fields.Date(
        string='Invoice date'
    )

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        journal_id = self.journal_id
        domain = {}
        value = {}
        active_ids = self._context.get('active_ids')
        if active_ids:
            picking = self.env['stock.picking'].browse(active_ids)
            type = picking.picking_type_id.code
            usage = picking.move_ids_without_package[0].location_id.usage if type == \
                'incoming' else picking.move_ids_without_package[0].location_dest_id.usage
            journal_types = map_journal_type.get(
                (type, usage), ['sale', 'purchase'])
            jou_typ = journal_types
            if jou_typ == ['purchase_refund']:
                jou_typ = ['purchase']
            elif jou_typ == ['sale_refund']:
                jou_typ = ['sale']
            domain['journal_id'] = [('type', 'in', jou_typ)]
        if journal_types not in ('sale_refund', 'purchase_refund'):
            if journal_id:
                value['journal_type'] = journal_id.type
        return {'value': value, 'domain': domain}

    def view_init(self, fields_list):
        res = super().view_init(fields_list)
        picking_obj = self.env['stock.picking']
        count = 0
        active_ids = self._context.get('active_ids')
        for pick in picking_obj.browse(active_ids):
            if pick.invoice_state != '2binvoiced':
                count += 1
        if len(active_ids) == count:
            raise ValidationError(_(u"None of these picking list \
                                  required invoicing"))
        return res

    @api.multi
    def open_invoice(self):
        invoice_ids = self.create_invoice()
        if not invoice_ids:
            raise ValidationError(_(u"No invoice create"))

        data = self[0]

        action = {}

        journal2type = {'sale': 'out_invoice', 'purchase': 'in_invoice',
                        'sale_refund': 'out_refund',
                        'purchase_refund': 'in_refund'}
        inv_type = journal2type.get(data.journal_type) or 'out_invoice'
        data_pool = self.env['ir.model.data']

        if inv_type == "out_invoice":
            action_id = data_pool.xmlid_to_res_id(
                'account.action_invoice_tree1')
        elif inv_type == "in_invoice":
            action_id = data_pool.xmlid_to_res_id(
                'account.action_invoice_tree2')
        elif inv_type == "out_refund":
            action_id = data_pool.xmlid_to_res_id(
                'account.action_invoice_tree1')
        elif inv_type == "in_refund":
            action_id = data_pool.xmlid_to_res_id(
                'account.action_invoice_tree2')

        if action_id:
            action_pool = self.env['ir.actions.act_window']
            action = action_pool.browse(action_id)
            return {
                'name': action[0].name,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', [x.id for x in invoice_ids])],
            }
        return True

    def create_invoice(self):
        ctx = dict(self._context)
        picking_obj = self.env['stock.picking']
        data = self[0]
        journal2type = {'sale': 'out_invoice', 'purchase': 'in_invoice',
                        'sale_refund': 'out_refund',
                        'purchase_refund': 'in_refund'}
        ctx['date_inv'] = data.invoice_date
        inv_type = journal2type.get(data.journal_type) or 'out_invoice'
        ctx['inv_type'] = inv_type

        active_ids = self._context.get('active_ids')
        ctx['active_ids'] = active_ids
        res = picking_obj.with_context(ctx).action_invoice_create(
            journal_id=data.journal_id.id,
            group=data.group,
            type=inv_type)
        return res
