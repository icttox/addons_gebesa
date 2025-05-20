# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseORder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def cancel_picking(self):
        self._cr.execute("""
            SELECT sp.id
            FROM stock_move AS sm
            JOIN stock_picking AS sp ON sm.picking_id = sp.id
                AND sp.state NOT IN ('done', 'cancel')
            JOIN purchase_order_line AS pol ON sm.purchase_line_id = pol.id
            JOIN purchase_order AS po ON pol.order_id = po.id
                AND po.state = 'cancel'""")
        if self._cr.rowcount:
            res = self._cr.fetchall()
            pickings = self.env['stock.picking'].search([('id', 'in', res)])
            pickings.action_cancel()

    @api.multi
    def action_rfq_send_new_button(self):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('purchase_order_gebesa', 'email_template_report_purchase_order')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'purchase.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'mark_rfq_as_sent': True,
        })

        # In the case of a RFQ or a PO, we want the "View..." button in line with the state of the
        # object. Therefore, we pass the model description in the context, in the language in which
        # the template is rendered.
        lang = self.env.context.get('lang')
        if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
            template = self.env['mail.template'].browse(ctx['default_template_id'])
            if template and template.lang:
                lang = template._render_template(template.lang, ctx['default_model'], ctx['default_res_id'])

        self = self.with_context(lang=lang)
        if self.state in ['draft', 'sent']:
            ctx['model_description'] = ('Request for Quotation')
        else:
            ctx['model_description'] = ('Purchase Order')

        return {
            'name': ('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
