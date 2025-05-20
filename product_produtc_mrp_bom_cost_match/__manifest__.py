# -*- coding: utf-8 -*-
# Copyright 2018, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Product BoM cost match',
    'summary': 'Run massively a cost match by product with their BoM',
    'version': '12.0.1.0.0',
    'category': 'Mrp',
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
        'base', 'stock_move_batch_validator'
    ],
    'data': [
        'data/match_costs_cron.xml',
        'wizards/product_product.xml',
    ],
    'demo': [
        # 'demo/res_partner_demo.xml',
    ],
    'qweb': [
        # 'static/src/xml/module_name.xml',
    ]
}
