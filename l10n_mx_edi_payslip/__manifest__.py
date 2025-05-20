# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Mexican Payroll",
    "version": "12.0.1.0.0",
    "author": "Vauxoo, Gebesa",
    "category": "Human Resources",
    "website": "http://vauxoo.com",
    "license": "OEEL-1",
    "depends": [
        "hr_payroll",
        "l10n_mx_base",
    ],
    "demo": [
        "demo/l10n_mx_payroll_employee_demo.xml",
        "demo/res_users_demo.xml",
        "demo/l10n_mx_payroll_cfdi0.xml",
        "demo/res_company_demo.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/payroll_paper_format.xml",
        "data/mail_template.xml",
        "views/hr_payslip_view.xml",
        "views/res_company.xml",
        "views/hr_contract_view.xml",
        "views/hr_payslip_report.xml",
        "data/hr_contract_type_data.xml",
        "data/hr_employee_data.xml",
        "data/salary_rule_data.xml",
        "data/fiscal_position_data.xml",
        "data/payroll_structure_data.xml",
    ],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False
}
