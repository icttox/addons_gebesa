# -*- coding: utf-8 -*-
# Copyright 2017, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Stock Account Gebesa',
    'summary': 'Generate Inventory account moves to fit to Gebesa Style',
    'version': '12.0.1.0.0',
    'category': 'Stock',
    'website': 'https://odoo-community.org/',
    'author': 'Cesar Barron, Gebesa',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'base',
        'stock',
        'stock_account',
        'stock_move_batch_validator'
    ],
    'data': [
        'wizards/stock_gebesa_view.xml',
    ],
    'demo': [
        'demo/res_partner_demo.xml',
    ],
    'qweb': [
        'static/src/xml/module_name.xml',
    ]
}
