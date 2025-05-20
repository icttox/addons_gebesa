# -*- coding: utf-8 -*-
# Copyright 2018, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res:
            res.force_lead_send()
        return res

    @api.multi
    def action_lead_sent(self):
        """ Open a window to compose an email, with the cfdi invoice template
            message loaded by default
        """

        self.ensure_one()

        mail_tmp_id = self.env.ref(
            'crm_lead_email_notification.email_template_lead_notification', False)

        compose_form = self.env.ref('mail.email_compose_message_wizard_form',
                                    False)

        ctx = dict(
            default_model='crm.lead',
            default_res_id=self.id,
            default_use_template=bool(mail_tmp_id),
            default_template_id=mail_tmp_id.id,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
        )
        return {
            'name': _('Compose Lead Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def force_lead_send(self):
        for lead in self:
            email_act = lead.action_lead_sent()
            if email_act and email_act.get('context'):
                email_ctx = email_act['context']
                email_ctx.update(default_email_from=lead.company_id.email)
                try:
                    lead.with_context(
                        email_ctx).message_post_with_template(
                        email_ctx.get('default_template_id'))
                except ValueError:
                    raise exceptions.ValidationError(_('Warning'), _(
                        'An error has occurred'))
        return True
