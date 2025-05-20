# -*- coding: utf-8 -*-
{
    'name': "send_alert_gebesa",
    'summary': "send_alert_gebesa",
    'description': "send_alert_gebesa",
    'version': "12.0.1.0.0",
    'category': "Personalized",
    'website': "https://odoo-community.org/",
    'author': "Marco Esquivel, Gebesa",
    "application": False,
    "installable": True,
    'depends': ['base', 'stock', 'sale', 'account', 'tms', 'quality', 'maintenance'],
    'data': [
        'data/ir_cron.xml'
    ],
    'demo': [
    ],
}
