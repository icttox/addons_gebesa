# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta
from odoo import models, fields, api


class SendAlertAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def send_alert_account(self):
        # import ipdb; ipdb.set_trace()
        companys = self.env['res.company'].search(
            [('is_manufacturer', '=', True)])

        customers = self.env['res.partner'].search(
            [('vat', 'in', ['CRE020718T31', 'ARM010910TL3', 'MMA891123689', 'RSL950503R10', 'EAN990529JJ7'])])

        product_ids = self.env['product.product']
        product_ids += self.env.ref('mpfproduct.scrap_carton_silleria')
        product_ids += self.env.ref('mpfproduct.scrap_carton_madera')
        product_ids += self.env.ref('mpfproduct.scrap_lamina')

        chanel_id = self.env.ref('mpfsaleschannel.internal')

        for company in companys:

            # sales = self.env['sale.order'].search(
            #     [('commitment_date', '!=', False)])

            day_day = datetime.today()
            invoices = self.search([
                ('type', '=', 'out_invoice'),
                ('state', 'in', ('open', 'paid')),
                ('prepayment_ok', '=', False),
                # ('sale_id', '!=', False),
                ('company_id', '=', company.id),
                ('date_invoice', '>=', day_day.date() - timedelta(days=8)),
                ('team_id', '!=', chanel_id.id),
                ('portfolio_type', '!=', 'street_market'),
                ('partner_id', 'not in', customers.ids)])

            table = ''
            on_time = 0
            late = 0
            fecha_com = 0
            inv_without_order = 0
            total_amount_invoiced = 0
            # import ipdb; ipdb.set_trace()
            for invoice in invoices:
                scrap = [scrap_id for scrap_id in product_ids.ids if scrap_id in invoice.invoice_line_ids.mapped('product_id').mapped('id')]
                if scrap:
                    continue
                limit_date = invoice.date_invoice
                days = day_day - fields.Datetime.from_string(limit_date)
                if invoice.sale_id.commitment_date:
                    date_commitment = invoice.sale_id.commitment_date
                    date_commit = fields.Date.from_string(date_commitment)
                    days_diferent = limit_date - date_commit
                    days_dif = days_diferent.days
                else:
                    date_commit = ''
                    days_dif = ''

                if invoice.sale_id.shipment_date:
                    shipment_date = invoice.sale_id.shipment_date
                    days_diferent = limit_date - shipment_date
                    days_shipment_dif = days_diferent.days
                else:
                    shipment_date = ''
                    days_shipment_dif = ''

                days = days.days
                if days <= 7:
                    if days_shipment_dif == '':
                        # fecha_com += 1
                        on_time += 1
                    elif days_shipment_dif > 0:
                        late += 1
                    elif days_shipment_dif <= 0:
                        on_time += 1

                    if not invoice.sale_id:
                        inv_without_order += 1

                    sale = invoice.sale_id
                    total_inv = invoice.amount_total * (invoice.rate_mex if invoice.rate_mex else 1.00)
                    total_so = sale.amount_total * (sale.rate_mex if sale.rate_mex else 1.00)

                    total_amount_invoiced += total_inv
                    # total_amount_invoiced = round((invoice.amount_total * 100) / total_amount_invoiced, 2)

                    table += """
                        <tr>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$ %s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        </tr>
                    """ % (
                        str(invoice.partner_id.name),
                        str(invoice.partner_dealer_id.name) if invoice.partner_dealer_id else '',
                        str(invoice.number),
                        '{:,.2f}'.format(total_inv),
                        str(sale.name) if sale else '',
                        '$ {:,.2f}'.format(total_so) if sale else '',
                        str(invoice.date_invoice),
                        str(date_commit) if sale else '',
                        str(shipment_date) if sale else '',
                        str(days_dif) if sale else '',
                        str(days_shipment_dif) if sale else '')

            sum_days = late + on_time + fecha_com
            porce_late = porce_on_time = porce_total = porce_sin_fecha = 0
            if sum_days > 0:
                porce_late = round((late * 100) / sum_days, 2)
                porce_on_time = round((on_time * 100) / sum_days, 2)
                porce_total = round((sum_days * 100) / sum_days, 2)
                # sum_fecha = sum_days + fecha_com
                # porce_sin_fecha = round((fecha_com * 100) / sum_days, 2)

            table_percent = """
                <tr>
                    <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">Entrega tarde</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s%%</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                </tr>
                <tr>
                    <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">Entrega a tiempo</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s%%</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                </tr>
                <!--tr>
                    <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">Entregas sin fechas compromiso</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s%%</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                </tr-->
                <tr>
                    <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">Total de entregas</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s%%</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                </tr>
                <tr>
                    <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">Facturas sin pedido</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';"></td>
                </tr>
                <tr>
                    <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">Monto total facturado</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$ %s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';"></td>
                </tr>
            """ % (porce_late, late, porce_on_time, on_time,
                   porce_sin_fecha, fecha_com,
                   porce_total, sum_days,
                   inv_without_order, '{:,.2f}'.format(total_amount_invoiced))

            body_mail = self.get_html_body_account_invoice(table, table_percent, company)
            destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_alert.shipments_in_time', 'False')
            self.send_alert_account_invoice(body_mail, destinatarios)

    def get_html_body_account_invoice(self, table=None, table_percent=None, company=None):
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
                margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Embarques a tiempo</b>
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
                            </strong></a> <br></br>
                            </p>
                        </td>
                    </tr>
                </tbody></table>
            </div>
            <br></br>
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
                margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:50%%;
                border-collapse:collapse; color:inherit">
                    <tbody>
                        <tr>
                            <th width="15%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                            border-bottom: 10px solid silver; background-color: #4f7ff4; color:ffffff">Entregas</th>
                            <th width="15%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                            border-bottom: 10px solid silver; background-color: #4f7ff4; color:ffffff"><strong>Porcentaje</strong></th>
                            <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                            border-bottom: 10px solid silver; background-color: #4f7ff4; color:ffffff"><strong>Cantidad</strong></th>
                        </tr>
                        %s
                    </tbody>
                </table>
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
                    <tbody>
                    <tr>
                        <th width="15%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Cliente</strong></th>
                        <th width="15%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Sub-Cliente</strong></th>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Folio factura</strong></th>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Monto factura</strong></th>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Folio pedido</strong></th>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Monto pedido</strong></th>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha factura</strong></th>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha compromiso</strong></th>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha Embarque</strong></th>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Diferencia días Programación a Entrega</strong></th>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Dias de diferencia</strong></th>
                    %s
                    </tbody>
                </table>
            </div>

          """ % (company.name, table_percent, table)
        return body_mail

    def send_alert_account_invoice(self, body_mail=None, destinatarios=None):
        mail = self.env['mail.mail'].create({
            'subject': 'Alerta de embarques a tiempo',
            'email_to': destinatarios,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()
