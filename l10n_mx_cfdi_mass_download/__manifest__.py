# Copyright 2022, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': "Cfdi Mass Download",

    'summary': """
        Make a mass CFDi download from SAT
        """,

    'description': """
        Make a mass CFDi download from SAT
    """,

    'author': "Cesar Barron",
    'website': "https://portal.e-fector.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['l10n_mx_edi_external_trade_geb'],

    'assets': {
        # 'web.assets_backend': [
        #     'l10n_mx_cfdi_mass_download/static/src/css/l10n_mx_cfdi_mass_download.css',
        #     'l10n_mx_cfdi_mass_download/static/src/js/custom.js',
        #     'l10n_mx_cfdi_mass_download/static/src/js/jszip.min.js',
        # ]
    },

    'data': [
        # # 'security/ir.model.access.csv',
        # 'views/res_config_settings_views.xml',
        'views/res_company_views.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/tab.xml'
    ],
    'demo': [
    ],
}
