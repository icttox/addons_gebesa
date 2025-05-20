# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def onchange_template_id(
            self, template_id, composition_mode, model, res_id):
        res = super(MailComposer, self).onchange_template_id(
            template_id, composition_mode, model, res_id)
        attachment_ids = res.setdefault('value', {}).setdefault(
            'attachment_ids', [])
        if model == 'account.invoice':
            invoice = self.env['account.invoice'].browse(res_id)
            name = "%s.xml" % invoice.l10n_mx_report_name
            xml_attachment = self.env['ir.attachment'].search([
                ('res_id', '=', res_id),
                ('res_model', '=', model),
                ('name', '=', name)], limit=1)
            if not xml_attachment:
                xml_attachment = invoice.generate_xml_attachment()
            if xml_attachment:
                attachment_ids.append((4, xml_attachment.id))
        return res
