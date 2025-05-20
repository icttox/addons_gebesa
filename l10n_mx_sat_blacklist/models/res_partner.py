# -*- coding: utf-8 -*-
# © 2016 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import csv
from odoo import _, api, fields, models
# import requests


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    sat_status = fields.Selection(
        [('definitivo', 'Definitivo'),
         ('desvirtuado', 'Desvirtuado'),
         ('presunto', 'Presunto'),
         ('favorable', 'Sentencia Favorable'),
         ('ninguno', 'Ninguno')],
        string=_(u"Situación del contribuyente"),
        default='ninguno',
    )

    @api.model
    def _get_sat_blacklist(self):
        """ Read the 'Blacklist' from SAT. """

        url = 'http://omawww.sat.gob.mx/cifras_sat/Documents/Listado_Completo_69-B.csv'
        response = urllib2.urlopen(url)
        cr = csv.reader(response)

        for row in cr:
            rfc = 'MX' + row[1]
            status = row[3]
            status = status.lower()
            if status == 'sentencia favorable':
                status = 'favorable'
            partner = self.env['res.partner'].search([('vat', '=', rfc),
                                                      ('active', '=', True)], limit=1)
            if partner:
                partner.write({'sat_status': status})

    @api.model
    def send_blacklist_alert(self):
        banned = self.search([('sat_status', 'in', ('definitivo', 'presunto'))])
        if not banned:
            return

        table = ''
        for partner in banned:
            table += """
                <tr><td align="center" style="border-bottom: 1px solid silver; font-size: 13px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; font-size: 13px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; font-size: 13px; font-family:'Arial';">%s</td>
                </tr>
            """ % (partner.vat, partner.name, partner.sat_status)
        mail_obj = self.env['mail.mail']
        body_mail = u"""
                    <div summary="o_mail_notification" style="padding:0px; width:100%%;
                     margin:0 auto; background: #FFFFFF repeat top /100%%; color:#77777
                     7">
                        <table cellspacing="0" cellpadding="0" style="width:100%%;
                        border-collapse:collapse; background:inherit; color:inherit">
                            <tbody><tr>
                                <td align="left" width="270" style="padding:5px 10px
                                 5px 5px;font-size: 15px; font-family:'Arial'">
                                    <p>Proveedores en lista negra del SAT</p>
                                </td>
                                <td align="right" align="right" width="310"
                                style="padding:5px 15px 5px 10px; font-size: 12px; font-family:'Arial'">
                                    <p>
                                    <strong>Sent by</strong>
                                    <a href="http://cfdi.e-fector.com" style="text-
                                    decoration:none; color: #a24689;">
                                        <strong>%s</strong>
                                    </a>
                                    </p>
                                </td>
                            </tr>
                        </tbody></table>
                    </div>
                    <div style="padding:0px; width:100%%; margin:0 auto; background:
                    #FFFFFF repeat top /100%%; color:#777777">
                        <table cellspacing="0" cellpadding="0" style="vertical-align:
                        top; padding:0px; border-collapse:collapse; background:inherit;
                         color:inherit; width:100%%;">
                            <tbody><tr>
                                <td valign="top" style="width:700px; padding:5px 10px
                                5px 5px; ">
                                    <div>
                                        <hr width="100%%" style="background-color:
                                        rgb(204,204,204);border:medium none;clear:both;
                                        display:block;font-size:0px;min-height:2px;
                                        line-height:0;margin:15px auto;padding:0">
                                    </div>
                                </td>
                            </tr></tbody>
                        </table>
                    </div>
                    <div style="padding:0px; width:100%%; margin:0 auto; background:
                    #FFFFFF repeat top /100%%;color:#777777">
                        <table style="border-collapse:collapse; margin: 0 auto; width: 100%%; background:inherit; color:inherit">
                            <tbody><tr>
                                <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                                border-bottom: 2px solid silver;"><strong>RFC</strong></th>
                                <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                                border-bottom: 2px solid silver;"><strong>Proveedor</strong></th>
                                <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                                border-bottom: 2px solid silver;"><strong>Situacion del contribuyente</strong></th>
                            </tr>
                            %s
                            </tbody>
                        </table>
                    </div>
                  """ % (self.env.user.company_id.name, table)
        mail = mail_obj.create({
            'subject': 'Proveedores en Lista Negra del SAT',
            'email_to': 'cesar.barron@gmail.com',
            'headers': "{'Return-Path': u'cesar.barron@gmail.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()

    # @api.model
    # def _get_sat_blacklist2(self):
    #     """ Read the 'Blacklist' from SAT. """
    #     csvurl = 'http://omawww.sat.gob.mx/cifras_sat/Documents/Listado_Completo_69-B.csv'

    #     with requests.Session() as s:
    #         download = s.get(csvurl)

    #         decoded_content = download.content.decode('utf-8')

    #         cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    #         my_list = list(cr)
    #         for row in my_list:
    #             rfc = row[1]
    #             status = row[3]
    #             status = status.lower()
    #             if status == 'sentencia favorable':
    #                 status = 'favorable'
    #             partner = self.env['res.partner'].search([('vat', '=', rfc),
    #                                                       ('active', '=', True)], limit=1)
    #             if partner:
    #                 partner.write({'sat_status': status})
