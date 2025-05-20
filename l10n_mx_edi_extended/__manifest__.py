# Copyright 2020, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Cfdi EDI extended",
    'version': '1.0',
    'author': 'Cesar Barron, Gebesa',
    'category': 'Hidden',
    'license': 'AGPL-3',
    'summary': """
        mx Cfdi Edi extension
    """,
    'depends': ['l10n_mx_edi',
                # 'l10n_mx_base',
                'invoice_refund_product_id',
                'multicurrency_mexico',
                'system_administrator',
                'sale',
                'account_invoice_replace'],
    'data': [
        'data/3.3/cfdi.xml',
        'data/3.3/payment10.xml',
        'data/4.0/cfdi.xml',
        'data/4.0/payment20.xml',
        'data/ir_cron_data.xml',
        'views/account_invoice_views.xml',
        'views/account_payment_views.xml',
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
        'wizard/account_invoice_refund.xml',
    ],

    'installable': True,
    'application': False,
    'demo': [],
    'test': []
}
