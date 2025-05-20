# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta, datetime
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _get_domain_groups_id(self):
        ids = self.env.ref('account_payment_auth.group_aut_pagos_super').ids
        return [('groups_id.id', '=', ids)]

    aut_estatus_pago = fields.Selection(
        [('none', 'None'),
         ('proposed', 'Proposed'),
         ('authorized', 'Authorized'),
         ('rejected', 'Rejected')],
        string="Payment authorization status",
        track_visibility='onchange',
        default='none',
    )
    authorizes_id = fields.Many2one(
        'res.users',
        string='Authorizes',
        domain=_get_domain_groups_id
    )

    @api.multi
    def action_payment_auth_request(self):
        limit_date = timedelta(days=3)
        # limit_date = fields.Date(default=3)
        currenty_date = datetime.now()
        # date_due_obj = self.env['account_invoice']
        # due = date_due_obj.browse(vals['date_due'])
        for invoice in self:
            # invoice.limit_date = (currenty_date).days + 3
            start = fields.Datetime.from_string(invoice.date_due)
            tot_date = start - limit_date
            if tot_date > currenty_date:
                raise ValidationError(_("Invoice does not expire yet"))
            if not invoice.authorizes_id.id:
                raise ValidationError(_("Error!\nField Authorized it's not \
                                      valid"))
            invoice.aut_estatus_pago = 'proposed'
        return True

    @api.multi
    def action_payment_auth(self):
        for invoice in self:
            if self.env.uid != invoice.authorizes_id.id:
                raise ValidationError(_("Error!\nYou may not authorize this \
                                      payment is not assigned to you"))
            invoice.aut_estatus_pago = 'authorized'
        return True

    @api.multi
    def action_refuse_payment(self):
        follower_ids = []
        for invoice in self:
            if self.env.uid != invoice.authorizes_id.id:
                raise ValidationError(_("Error!\nYou can not refuse this \
                                      payment is not assigned to you"))
            invoice.aut_estatus_pago = 'rejected'
            for follower in invoice.message_follower_ids:
                if follower.partner_id.user_ids:
                    follower_ids.append(follower.partner_id.id)
        compose_form = self.env.ref(
            'mail.email_compose_message_wizard_form',
            False)

        ctx = dict(
            default_partner_ids=follower_ids,
        )
        return {
            'name': _('Compose CFDI Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
