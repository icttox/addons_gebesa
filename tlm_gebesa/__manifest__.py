# -*- coding: utf-8 -*-
{
    'name': "tlm_gebesa",

    'summary': """
        Travel Life Magnament""",

    'description': """
        Travel Life Magnament
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
        "base",
        "flete_gebesa",
        "tms",
                ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/tms_travel_view.xml',
        'security/security.xml',
        'security/ir.model.access.csv',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
