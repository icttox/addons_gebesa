# -*- coding: utf-8 -*-
{
    'name': "Send Email Purchases Payments",
    'summary': "Send Alert Purchases/Payments",
    'version': '12.0',
    'description': "Send Alert By Mail Purchases/Payments Of Partner Novapack",
    'author': "Marco Esquivel, Gebesa",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'depends': ['base', 'purchase', 'account', 'account_register_payments_line'],
    'data': [
        'views/res_partner_view.xml',
        'data/ir_cron.xml',
    ],
    'demo': [
    ],
}
