# -*- coding: utf-8 -*-
# Copyright 2017, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale Order Product Validator',
    'summary': 'Validate data from product product',
    'version': '12.0.1.0.0',
    'category': 'sale',
    'website': 'https://odoo-community.org/',
    'author': '2017, Cesar Barron, Gebesa',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'base', 'sale',
        'res_company_manufacturer',
        'product_structure_gebesa',
    ],
    'data': [
        "views/sale_order.xml",
        "data/mail_template.xml"
    ],
    'demo': [
        # 'demo/res_partner_demo.xml',
    ],
    'qweb': [
        # 'static/src/xml/module_name.xml',
    ]
}
