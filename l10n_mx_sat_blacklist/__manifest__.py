# -*- coding: utf-8 -*-
# Copyright 2020, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'SAT Black List Sync',
    'summary': 'Download the SAT Black list and Sync with partners',
    'version': '12.0.1.0.0',
    'category': 'account',
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
        'base', 'account'
    ],
    'data': [
        'data/sat_blacklist_read.xml',
        'views/res_partner_views.xml',
    ],
    'demo': [
        # 'demo/res_partner_demo.xml',
    ],
    'qweb': [
        # 'static/src/xml/module_name.xml',
    ]
}
