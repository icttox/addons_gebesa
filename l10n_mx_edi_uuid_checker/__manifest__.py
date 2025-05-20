# -*- coding: utf-8 -*-
{
    'name': "l10n_mx_edi_uuid_checker",

    'summary': """
        l10n mx edi uuid checker""",

    'description': """
        l10n mx edi uuid checker
    """,

    'author': "Leslie Marquez, Gebesa",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizards/l10n_mx_edi_uuid_checker_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
