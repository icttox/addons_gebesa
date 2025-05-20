# -*- coding: utf-8 -*-
# © 2021, Leslie Marquez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date, timedelta
from odoo import fields, models, api
from num2words import num2words


class HrContract(models.Model):
    _inherit = 'hr.contract'

    credito_infonavit = fields.Boolean(
        string='Infonavit Credit',
        default=False
    )

    credito_fonacot = fields.Boolean(
        string='Fonacot Credit',
        default=False
    )

    premio_asistencia = fields.Float(
        string='Assistance award',
    )

    premio_puntualidad = fields.Float(
        string='Punctuality award',
    )

    incentivo = fields.Float(
        string='Incentivo',
    )

    salario_diario = fields.Monetary(
        'Daily Salary',
        digits=(16, 2),
        required=True,
    )

    company = fields.Char(
        company_dependent=True,
        string="Company Witness",
    )

    witness_rh = fields.Char(
        company_dependent=True,
        string="Witness RH",
    )

    witness = fields.Char(
        company_dependent=True,
        string="Witness",
    )

    date_trial_start = fields.Date(
        'Start of Trial Period',
        help="Start date of the trial period (if there is one)."
    )

    @api.model
    def calcular_sueldo(self):
        pantry_bonus = self.env['ir.config_parameter'].sudo().get_param('rh_gebesa.amount_of_the_pantry_bonus')
        sueldo_numerico = round((self.salario_diario * 7) + self.premio_puntualidad + self.premio_asistencia + float(pantry_bonus), 2)
        sueldo_palabras = num2words(sueldo_numerico, lang='es')
        return sueldo_numerico, sueldo_palabras

    @api.onchange('job_id')
    def onchange_job_salaries(self):
        if self.job_id and self.job_id.wage > 0:
            self.wage = self.job_id.wage
        if self.job_id and self.job_id.daily_salary > 0:
            self.salario_diario = self.job_id.daily_salary
        if self.job_id and self.job_id.assistance_award > 0:
            self.premio_asistencia = self.job_id.assistance_award
        if self.job_id and self.job_id.punctuality_award > 0:
            self.premio_puntualidad = self.job_id.punctuality_award

    @api.model
    def send_contract(self):
        # mes_1_concluido = fields.Date.to_string(date.today() + timedelta(days=1))
        # mes_2_concluido = fields.Date.to_string(date.today() - timedelta(days=1))
        companys = self.env['res.company'].search(
            [('id', '!=', 4)])
        for company in companys:

            contrato = self.env['hr.contract'].search([
                ('state', 'not in', ['close', 'cancel']),
                ('company_id', '=', company.id)
            ])

            # destdefault = 'leticia.lopez@gebesa.com, daniela.luna@gebesa.com, olaff.munoz@gebesa.com, judith.nava@gebesa.com, jacqueline.flores@gebesa.com, cesar.barron@gebesa.com'

            destinatarios = self.env['ir.config_parameter'].sudo().get_param('rh_gebesa.receivers_email_dest_' + str(company.id), 'False')

            mes_vencido_1 = contrato.filtered(lambda ct: ct.date_start == (date.today() - timedelta(days=28)))
            mes_vencido_2 = contrato.filtered(lambda ct: ct.date_start == (date.today() - timedelta(days=58)))

            table = ''
            for rec in mes_vencido_1:
                departamento = rec.department_id.name if rec.department_id.name else ''
                table += """
                    <tr><td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    </tr>
                """ % (
                    rec.name, rec.employee_id.name, rec.company_id.name,
                    str(departamento), rec.job_id.name,
                    rec.date_start)
            if table:
                body_mail = self.get_html_body(table, company)
                # destinatarios = destdefault
                self.send_alert(body_mail, destinatarios, 'Reporte del Segundo Contrato por Concluir')
            table = ''
            for reco in mes_vencido_2:
                departamento_nombre = reco.department_id.name if reco.department_id.name else ''
                table += """
                    <tr><td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    </tr>
                """ % (
                    reco.name, reco.employee_id.name, reco.company_id.name,
                    str(departamento_nombre), reco.job_id.name,
                    reco.date_start)
            if table:
                body_mail = self.get_html_body(table, company)
                # destinatarios = destdefault
                self.send_alert(body_mail, destinatarios, 'Reporte del Tercer Contrato por Concluir')

    def get_html_body(self, table=None, company=False):
        if not company:
            company = self.env.user.company_id
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
            margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Contratos por Concluir</b>
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
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Contrato</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Empleado</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Compañia</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Departamento</strong></th>
                        <th width="12%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Puesto</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha de Ingreso</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (company.name, table)
        return body_mail

    def send_alert(self, body_mail=None, destinatarios=None, titulo=None):
        mail = self.env['mail.mail'].create({
            'subject': titulo,
            'email_to': destinatarios,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()
