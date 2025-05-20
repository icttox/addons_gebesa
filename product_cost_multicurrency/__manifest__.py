# -*- coding: utf-8 -*-
{
    'name': "product_cost_multicurrency",

    'summary': """
        Product Cost Multicurrency""",

    'description': """
        Product Cost Multicurrency
    """,

    'author': "Leslie Marquez, Gebesa",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'system_administrator'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/product_cost_multicurrency_view.xml',
        'data/ir_cron.xml'
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
