# -*- coding: utf-8 -*-
{
    'name': "send_alert_account_invoice",
    'summary': "send_alert_account_invoice",
    'description': "send_alert_account_invoice",
    'version': "12.0.1.0.0",
    'category': "Personalized",
    'website': "https://odoo-community.org/",
    'author': "Marco Esquivel, Gebesa",
    "application": False,
    "installable": True,
    'depends': ['base', 'account'],
    'data': [
        'data/ir_cron.xml'
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
