# -*- coding: utf-8 -*-
{
    'name': "gebesallc_reports",

    'summary': """
        Gebesa LLC Reports""",

    'description': """
        Gebesa LLC Reports
    """,

    'author': "My Company, Gebesa",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/config_data.xml',
        'reports/account_invoice_report.xml',
        'reports/advance.xml',
        'security/security.xml',
        'views/account_invoice_view.xml',
        'views/sale_order_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
