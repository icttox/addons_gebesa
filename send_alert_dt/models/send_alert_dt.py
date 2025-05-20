# -*- coding: utf-8 -*-

from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def send_email_dt_alert(self):
        self._cr.execute(
            """SELECT pp.name_template, pp.default_code, COUNT (mb.id)
                FROM mrp_bom AS mb
                LEFT JOIN product_product AS pp ON pp.id = mb.product_id
                WHERE mb.active = TRUE
                GROUP BY pp.id
                HAVING COUNT(mb.id) > 1""")
        if not self._cr.rowcount:
            return
        product = self._cr.fetchall()
        table = ''
        for duplicate in product:
            table += """
                <tr><td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                </tr>
                """ % (duplicate[0], duplicate[1], duplicate[2])
        mail_obj = self.env['mail.mail']
        body_mail = u"""
                            <div summary="o_mail_notification" style="padding:0px; width:90%%;
             margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Detalles Duplicados</b>
                        </td>
                        <td valign="center" align="right" width="270"
                        style="padding:5px 15px 5px 10px; font-family:'Arial'; font-size: 12px;">
                            <p>
                            <strong>Sent by</strong>
                            <a href="http://erp.portalgebesa.com" style="text-
                            decoration:none; color: #a24689; font-family:'Arial';">
                                <strong>%s</strong>
                            </a>
                            <strong>using</strong>
                            <a href="https://www.odoo.com" style="text-
                            decoration:none; color: #a24689;"><strong>Odoo
                            </strong></a>
                            </p>
                        </td>
                    </tr>
                </tbody></table>
            </div>
            <div style="padding:0px; width:900px; margin:0 auto; background:
            #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="vertical-align:
                top; padding:0px; border-collapse:collapse; background:inherit;
                 color:inherit">
                    <tbody><tr>
                        <td valign="top" style="width:70%%; padding:5px 10px
                        5px 5px; ">
                            <div>
                                <hr width="900px" style="background-color:
                                rgb(204,204,204);border:medium none;clear:both;
                                display:block;font-size:0px;min-height:1px;
                                line-height:0;margin:15px auto;padding:0">
                            </div>
                        </td>
                    </tr></tbody>
                </table>
            </div>
            <div style="padding:0px; width:100%%; margin:0 auto; background:
            #FFFFFF repeat top /100%%; color:#fff">
                <table style="border-collapse:collapse; margin: 0 auto; width:
                90%%; background:inherit; color:inherit">
                    <tbody><tr>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Clave del producto</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Nombre del producto</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Detalles duplicados</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (self.env.user.company_id.name, table)
        destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_alert_dt.receivers_email', 'False')
        mail = mail_obj.create({
            'subject': 'Detalles duplicados',
            'email_to': destinatarios,
            # 'email_to': 'viridiana.gamon@gebesa.com, deysy.mascorro@gebesa.com, cesar.barron@gebesa.com, esmeralda.gutierrez@gebesa.com',
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()
