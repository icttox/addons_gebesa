
# -*- coding: utf-8 -*-
# © 2020 Samuel Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from odoo import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def sent_supplier_attachment(self, email_to=False):
        attachments = self.env['ir.attachment']

        result, format = self.env.ref('report_last_attachment.supplier_attachment').render_qweb_pdf(self)

        result = base64.b64encode(result)
        attachments += attachments.create({
            'datas': result,
            'name': 'Ultimos Adjuntos por Proveedor',
            'datas_fname': '%s.%s' % ('Ultimos Adjuntos por Proveedor', format),
        })
        # import ipdb; ipdb.set_trace()
        mail_obj = self.env['mail.mail']

        if not email_to:
            email_to = 'cesar.barron@gebesa.com,deysy.mascorro@gebesa.com,samuel.barron@gebesa.com'

        mail = mail_obj.create({
            'subject': 'Ultimo Adjunto de Proveedores',
            'email_to': email_to,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': '<p>Se adjunta el pdf del ultimo archivo adjunto de cada proveedor</p>',
            'auto_delete': True,
            'message_type': 'comment',
            'attachment_ids': [(6, 0, attachments.ids)],
        })
        mail.send()
        return True
