# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Stock Picking Account Move Batch',
    'summary': 'Stock Picking Account Move Batch',
    'version': '12.0.1.0.0',
    'category': 'Account',
    'website': 'https://odoo-community.org/',
    'author': 'Samuel Barron, Gebesa',
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
        'stock_picking_account_location',
        "stock_move_batch_validator",
    ],
    'data': [
        "wizards/batch_picking_account.xml",
    ],
    'demo': [
    ],
    'qweb': [
    ]
}
