# -*- coding: utf-8 -*-
{
    'name': "Waybill Complement For non carriers",

    'summary': """
        L10n Mx Edi Waybill Complement for non carriers""",

    'description': """
        L10n Mx Edi Waybill Complement for non carriers
    """,

    'author': "Cesar Barron, Gebesa",
    'website': "http://www.gebesa.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
        'base',
        'l10n_mx_edi_waybill_complement'],

    'data': [
        'views/account_invoice_views.xml',
        'views/product_template_views.xml',
        'data/2.0/stores_waybill20.xml',
        'reports/report_invoice.xml',
        'views/tms_place_view.xml',
        'views/fleet_vehicle_view.xml',
        'security/waybill_security.xml',
    ],
    'demo': [

    ],
}
