# -*- coding: utf-8 -*-
# Copyright 2018, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'CRM Lead mail notification',
    'summary': 'This module sends email notification when a new lead is created',
    'version': '12.0.1.0.0',
    'category': 'CRM',
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
        'base', 'crm', 'leads_gebesa'
    ],
    'data': [
        'data/mail_template_data.xml',
    ],
    'demo': [
        # 'demo/res_partner_demo.xml',
    ],
    'qweb': [
        # 'static/src/xml/module_name.xml',
    ]
}
