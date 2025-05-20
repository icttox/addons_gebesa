# -*- coding: utf-8 -*-
# Copyright 2018, Samuel Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Product product balance',
    'summary': 'Dayly summarize of product product balance',
    'version': '12.0.1.0.0',
    'category': 'Product',
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
        'product',
        'stock',
    ],
    'data': [
        'data/ir_cron_data.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ]
}
