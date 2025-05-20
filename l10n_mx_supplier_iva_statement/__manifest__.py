# -*- coding: utf-8 -*-
# Copyright 2020, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Supplier taxes statement',
    'summary': 'Provides all necesary for monthly taxes declaration',
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
        'reports/account_move_report.xml',
        'reports/account_voucher_report.xml',
        'wizards/l10n_mx_supplier_taxes_master_view.xml',
        'data/config_parameter.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ]
}
