# -*- coding: utf-8 -*-
# Copyright 2017, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Website Quotation Avoid Customer Actions',
    'summary': 'This module avoids the customer can validate SO online',
    'version': '12.0.1.0.0',
    'category': 'Website',
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
        # 'website_quote'
    ],
    'data': [
        # 'view/some_model_view.xml',
    ],
    'demo': [
        'demo/res_partner_demo.xml',
    ],
    'qweb': [
        'static/src/xml/module_name.xml',
    ]
}
