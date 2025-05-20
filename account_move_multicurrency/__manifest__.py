# -*- coding: utf-8 -*-
{
    'name': "Account Move Multicurrency",

    'summary': """
        Allow users regiser account moves in foreign currency""",

    'author': "Leslie Marquez, Gebesa",
    'website': "http://www.yourcompany.com",
    'category': 'Account',
    'version': '0.1',

    'depends': ['base', 'account'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_move_multicurrency_view.xml',
        'views/account_move_multicurrency_secuence.xml',
        'views/reports.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
