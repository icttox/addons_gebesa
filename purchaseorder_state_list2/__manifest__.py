# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Purchase Order State Hist',
    'summary': 'Purchase Order State Hist',
    'version': '12.0.1.0.0',
    'category': 'Purchase',
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
        'purchase'
    ],
    'data': [
        'views/purchaseorder_state_hist_view.xml',
        'views/purchase_order_view.xml',
        'security/ir.model.access.csv',


    ],
    'demo': [

    ],
    'qweb': [

    ]
}
