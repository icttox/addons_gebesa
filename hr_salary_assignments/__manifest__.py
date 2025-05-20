{
    'name': "HR Salary assing",
    'summary': "Module to calculate assing in payrroll",
    'author': "Marco Esquivel, Gebesa",
    'website': "http://www.yourcompany.com",
    'category': 'Installer',
    'version': '12.0',
    'depends': [
        'hr_payroll',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/server_action.xml',
        # 'views/assets.xml',
        'views/salary_assignments_view.xml',
        'views/hr_payslip.xml',
        'views/salary_assignments_batches_view.xml',
        'views/hr_salary_rule.xml',
        'views/hr_contract.xml',
        # 'wizards/wizard_salary_assingments_xls.xml',
        'wizards/txt_report_wizard.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'qweb': [
        # 'static/src/xml/tree_view_buttons.xml'
    ],
}
