# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Stock move view sale',
    'summary': 'Stock move view sale',
    'version': '12.0.1.0.0',
    'category': 'stock',
    'website': 'https://odoo-community.org/',
    'author': 'Eduardo Lopez, Gebesa',
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
    ],
    'data': [
        'views/stock_move_view_sale.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ]
}
