from odoo import api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _description = "Purchase Order"

    revision = fields.Integer(string='Amendment Revision')
    state = fields.Selection(selection_add=[('amendment', 'Amendment')])
    amendment_name = fields.Char('Order Reference', copy=True, readonly=True)
    current_amendment_id = fields.Many2one(
        'purchase.order', 'Current Amendment', readonly=True, copy=True)
    old_amendment_ids = fields.One2many(
        'purchase.order', 'current_amendment_id', 'Old Amendment',
        readonly=True, context={'active_test': False})

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if not res.amendment_name:
            res.amendment_name = res.name
        return res

    @api.returns('self', lambda value: value.id)
    @api.multi
    def copy(self, defaults=None):
        if not defaults:
            defaults = {}
        if self.env.context.get('new_purchase_amendment'):
            prev_name = self.name
            revno = self.revision
            # Assign default values for views
            self.write({
                'revision': revno + 1,
                'name': '%s-%02d' % (self.name, revno + 1)})
            defaults.update({
                'name': prev_name, 'revision': revno,
                'state': 'cancel', 'invoice_count': 0,
                'current_amendment_id': self.id,
                'amendment_name': self.amendment_name})
        return super(PurchaseOrder, self).copy(defaults)

    def button_amend(self):
        for purchase in self:
            for picking_loop in purchase.picking_ids:
                if picking_loop.state == 'done':
                    raise UserError('Unable to amend this purchase order, You must first cancel all receptions related to this purchase order.')
                picking_loop.filtered(lambda r: r.state != 'cancel').action_cancel()

            for invoice_loop in purchase.invoice_ids:
                if invoice_loop.state != 'draft':
                    raise UserError('Unable to amend this purchase order, You must first cancel all Supplier Invoices related to this purchase order.')
                invoice_loop.filtered(lambda r: r.state != 'cancel').action_invoice_cancel()
        # self.button_draft()
        self.with_context(new_purchase_amendment=True).copy()
        self.write({'state': 'amendment'})
