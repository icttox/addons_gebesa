# -*- coding: utf-8 -*-
{
    'name': "run_sql_serverside",

    'summary': """
        Run Sql Serverside""",

    'description': """
        Run Sql Serverside
    """,

    'author': "Leslie Marquez, Gebesa",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'system_administrator',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizards/run_sql_serverside_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
