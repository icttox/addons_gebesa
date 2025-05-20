# -*- coding: utf-8 -*-
# Copyright 2018, Samuel Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Property view',
    'summary': 'Inherit view ir.property',
    'version': '12.0.1.0.0',
    'category': 'Basw',
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
    ],
    'data': [
        'views/ir_property.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ]
}
