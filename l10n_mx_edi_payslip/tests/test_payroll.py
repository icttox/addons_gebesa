# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os
import base64

from datetime import datetime, timedelta
from lxml import objectify

import odoo

from odoo.tests.common import TransactionCase


class HRPayroll(TransactionCase):

    def setUp(self):
        super(HRPayroll, self).setUp()
        self.payslip_obj = self.env['hr.payslip']
        self.mail_obj = self.env['mail.compose.message']
        self.payslip_run_obj = self.env['hr.payslip.run']
        self.wizard_batch = self.env['hr.payslip.employees']

        self.employee = self.env.ref('hr.employee_qdp')
        self.contract = self.env.ref('hr_payroll.hr_contract_gilles_gravie')
        self.struct = self.env.ref(
            'l10n_mx_edi_payslip.payroll_structure_data_01')
        self.pac = self.env.ref('l10n_mx_base.pac_vauxoo')
        self.sequence = self.env.ref('hr_payroll.seq_salary_slip')
        self.cat_excempt = self.env.ref(
            'l10n_mx_edi_payslip.hr_salary_rule_category_perception_mx_exempt')

        xml_expected_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'expected_cfdi.xml')
        xml_expected_f = open(xml_expected_path)
        self.xml_expected = objectify.parse(xml_expected_f).getroot()
        self.env.ref('l10n_mx_base.l10n_mx_edi_version_cfdi').value = '3.3'

    def test_001_xml_structure(self):
        """Use XML expected to verify that is equal to generated. And SAT
        status"""
        payroll = self.create_payroll()
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'signed',
                          payroll.message_ids.mapped('body'))
        payroll.l10n_mx_edi_update_sat_status()
        self.assertEquals(payroll.l10n_mx_edi_sat_status, 'not_found')
        xml_signed = payroll.l10n_mx_edi_cfdi
        xml = objectify.fromstring(base64.decodestring(xml_signed))
        payroll = xml.Complemento.xpath(
            'nomina12:Nomina',
            namespaces={'nomina12': 'http://www.sat.gob.mx/nomina12'})[0]
        self.assertIsNotNone(payroll, 'Complement to payroll not added.')
        self.xml_expected.Receptor.attrib['FechaInicioRelLaboral'] = payroll.Receptor.attrib['FechaInicioRelLaboral']  # noqa
        self.xml_expected.attrib['FechaFinalPago'] = payroll.attrib['FechaFinalPago']  # noqa
        self.xml_expected.attrib['FechaInicialPago'] = payroll.attrib['FechaInicialPago']  # noqa
        self.xml_expected.attrib['FechaPago'] = payroll.attrib['FechaPago']
        self.xml_expected.Receptor.attrib[u'Antig\xfcedad'] = payroll.Receptor.attrib[u'Antig\xfcedad']  # noqa
        self.assertEqualXML(payroll[0], self.xml_expected)

    def test_002_error_signed(self):
        """Try validate the payroll without CURP employee, the PAC status
        must be retry because the CFDI was not generated"""
        self.employee.l10n_mx_edi_curp = ''
        payroll = self.create_payroll()
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'retry')

    def test_003_inactive_pac(self):
        """Try validate the payroll without PAC, the PAC status
        must be retry."""
        self.sequence.pac_id = False
        payroll = self.create_payroll()
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'retry')
        self.sequence.pac_id = self.pac.id
        payroll.l10n_mx_edi_update_pac_status()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'signed',
                          payroll.message_ids.mapped('body'))

    def test_004_perception_022(self):
        """When perception code have 022, the payroll have node
        SeparacionIndemnizacion."""
        payroll = self.create_payroll()
        payroll.write({
            'input_line_ids': [(0, 0, {
                'code': 'pe_022',
                'name': u'Prima por antigüedad',
                'amount': 1000.0,
                'contract_id': self.contract.id,
            })],
            'l10n_mx_edi_extra_node_ids': [(0, 0, {
                'node': 'separation',
                'amount_total': 1000.0,
                'service_years': 5.0,
                'last_salary': 1000.0,
                'accumulable_income': 900.0,
                'non_accumulable_income': 100.0,
            })],
        })
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'signed',
                          payroll.message_ids.mapped('body'))

    def test_005_perception_039(self):
        """When perception code have 039, the payroll have node
        JubilacionPensionRetiro."""
        payroll = self.create_payroll()
        payroll.write({
            'input_line_ids': [(0, 0, {
                'code': 'pe_039',
                'name': u'Jubilaciones, pensiones o haberes de retiro',
                'amount': 1000.0,
                'contract_id': self.contract.id,
            })],
            'l10n_mx_edi_extra_node_ids': [(0, 0, {
                'node': 'retirement',
                'amount_total': 1000.0,
                'accumulable_income': 900.0,
                'non_accumulable_income': 100.0,
            })],
        })
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'signed',
                          payroll.message_ids.mapped('body'))

    def test_006_other_payment_002(self):
        """When other payment have the code 002, this must have node
        SubsidioAlEmpleo."""
        payroll = self.create_payroll()
        payroll.write({
            'input_line_ids': [(0, 0, {
                'code': 'op_002',
                'name': u'Subsidio para el empleo',
                'amount': 500.0,
                'contract_id': self.contract.id,
            })],
            'l10n_mx_edi_subsidy': 500.0,
        })
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'signed',
                          payroll.message_ids.mapped('body'))

    def test_007_other_payment_004(self):
        """When other payment have the code 004, this must have node
        CompensacionSaldosAFavor."""
        payroll = self.create_payroll()
        payroll.write({
            'input_line_ids': [(0, 0, {
                'code': 'op_004',
                'name': u'Aplicación de saldo a favor por compensación anual.',
                'amount': 500.0,
                'contract_id': self.contract.id,
            })],
            'l10n_mx_edi_balance_favor': 500.0,
            'l10n_mx_edi_comp_year': 2016,
            'l10n_mx_edi_remaining': 500.0,
        })
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'signed',
                          payroll.message_ids.mapped('body'))

    def test_008_without_certificate(self):
        """Try validate the payroll without Certificate, the PAC status
        must be retry."""
        payroll = self.create_payroll()
        payroll.company_id.certificate_id = False
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'retry')

    def test_009_perception_045(self):
        """When one perception have the code 045, this must have node
        AccionesOTitulos,."""
        payroll = self.create_payroll()
        payroll.write({
            'input_line_ids': [(0, 0, {
                'code': 'pe_045',
                'name': u'Ingresos en acciones o títulos valor que representan bienes',  # noqa
                'amount': 500.0,
                'contract_id': self.contract.id,
            })],
            'l10n_mx_edi_action_title_ids': [(0, 0, {
                'category_id': self.cat_excempt.id,
                'market_value': 100.0,
                'price_granted': 100.0,
            })]
        })
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'signed',
                          payroll.message_ids.mapped('body'))

    def test_010_payroll_wo_contract(self):
        """Try generate CFDI withou employee contracts"""
        payroll = self.create_payroll()
        employee = self.employee.copy()
        payroll.employee_id = employee
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'retry')

    def test_011_print_pdf(self):
        """Verify that PDF is generated"""
        payroll = self.create_payroll()
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'signed',
                          payroll.message_ids.mapped('body'))
        report = odoo.report.render_report(
            self.cr, self.uid, payroll.ids, 'hr_payroll.report_payslip',
            {'model': 'hr.payslip'}, context=self.env.context)
        self.assertTrue(report, 'Report not generated.')

    def test_012_cancel_xml(self):
        """Verify that XML is cancelled"""
        payroll = self.create_payroll()
        payroll.action_payslip_cancel()
        payroll.action_payslip_draft()
        payroll.action_payslip_done()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'signed',
                          payroll.message_ids.mapped('body'))
        payroll.action_payslip_cancel()
        self.assertEquals(payroll.l10n_mx_edi_pac_status, 'cancelled')

    def test_013_send_payroll_mail(self):
        """Verify that XML is attach on wizard that send mail"""
        payroll = self.create_payroll()
        payroll.action_payslip_done()
        mail_data = payroll.action_payroll_sent()
        template = mail_data.get('context', {}).get('default_template_id', [])
        template = self.env['mail.template'].browse(template)
        mail = template.generate_email(payroll.ids)
        self.assertEquals(len(mail[payroll.id].get('attachments')), 2,
                          'Documents not attached')

    def test_014_batches(self):
        """Verify payroll information from batches"""
        date = (datetime.today() + timedelta(days=5)).strftime('%Y-%m-%d')
        payslip_run = self.payslip_run_obj.create({
            'name': 'Payslip VX',
            'l10n_mx_edi_payment_date': date,
        })
        self.wizard_batch.create({
            'employee_ids': [(6, 0, self.employee.ids)]
        }).with_context(active_id=payslip_run.id).compute_sheet()
        self.assertEquals(payslip_run.slip_ids.l10n_mx_edi_payment_date, date,
                          'Payment date not assigned in the payroll created.')

    def create_payroll(self):
        return self.payslip_obj.create({
            'name': 'Payslip Test',
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.struct.id,
            'l10n_mx_edi_source_resource': 'IP',
            'worked_days_line_ids': [(0, 0, {
                'name': 'Normal Working Days',
                'code': 'TESTNW',
                'number_of_days': 15,
                'number_of_hours': 40,
                'contract_id': self.contract.id,
            })],
            'input_line_ids': [(0, 0, {
                'code': 'pg_001',
                'name': 'Sueldos, Salarios Rayas y Jornales',
                'amount': 12500.0,
                'contract_id': self.contract.id,
            }), (0, 0, {
                'code': 'pe_005',
                'name': 'Fondo de Ahorro',
                'amount': 200.0,
                'contract_id': self.contract.id,
            }), (0, 0, {
                'code': 'pg_019',
                'name': 'Horas extra',
                'amount': 300.0,
                'contract_id': self.contract.id,
            }), (0, 0, {
                'code': 'd_001',
                'name': 'Seguridad social',
                'amount': 300.0,
                'contract_id': self.contract.id,
            }), (0, 0, {
                'code': 'd_002',
                'name': 'ISR',
                'amount': 2000.0,
                'contract_id': self.contract.id,
            }), (0, 0, {
                'code': 'd_006',
                'name': 'Descuento por incapacidad',
                'amount': 100.0,
                'contract_id': self.contract.id,
            }), (0, 0, {
                'code': 'op_003',
                'name': u'Viáticos',
                'amount': 300.0,
                'contract_id': self.contract.id,
            })],
            'l10n_mx_edi_inability_line_ids': [(0, 0, {
                'amount': 100.0,
                'days': 1,
                'inability_type': '02',
            })],
            'l10n_mx_edi_overtime_line_ids': [(0, 0, {
                'amount': 300.0,
                'name': 'Overtime Test',
                'days': 1,
                'hours': 1,
                'overtime_type': '02',
            })],
        })

    def xml2dict(self, xml):
        """Receive 1 lxml etree object and return a dict string.
        This method allow us have a precise diff output"""
        def recursive_dict(element):
            return (element.tag,
                    dict(map(recursive_dict, element.getchildren()),
                         **element.attrib))
        return dict([recursive_dict(xml)])

    def assertEqualXML(self, xml_real, xml_expected):
        """Receive 2 objectify objects and show a diff assert if exists."""
        xml_expected = self.xml2dict(xml_expected)
        xml_real = self.xml2dict(xml_real)
        # noqa "self.maxDiff = None" is used to get a full diff from assertEqual method
        # This allow us get a precise and large log message of where is failing
        # expected xml vs real xml More info:
        # noqa https://docs.python.org/2/library/unittest.html#unittest.TestCase.maxDiff
        self.maxDiff = None
        self.assertEqual(xml_real, xml_expected)
