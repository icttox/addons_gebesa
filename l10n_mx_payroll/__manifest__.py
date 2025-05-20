# -*- coding: utf-8 -*-
{
    'name': "L10n_mx_payroll",
    'summary': "L10n_mx_payroll",
    'version': '12.0',
    'description': "sin description",
    'author': "Marco Esquivel, Gebesa",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'depends': ['base', 'hr_payroll'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/l10n_mx_isr_view.xml',
        'views/l10n_mx_isr_detail_view.xml',
        'views/l10n_mx_subemp_view.xml',
        'views/l10n_mx_subemp_line_view.xml',
        'views/l10n_mx_senority_table_view.xml',
        'views/l10n_mx_senority_table_line_view.xml',
        'views/l10n_mx_minimum_wages_view.xml',
        'views/l10n_mx_minimum_wages_line_view.xml',
    ],
    'demo': [
    ],
}
