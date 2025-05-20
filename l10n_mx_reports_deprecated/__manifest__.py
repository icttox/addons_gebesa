# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Odoo Mexican Localization Reports",
    "summary": """
        Electronic accounting reports
            - COA
            - Trial Balance
            - Journal Items
        DIOT Report
    """,
    "version": "12.0.1.0.0",
    "author": "Vauxoo, Gebesa",
    "category": "Accounting",
    "website": "http://www.vauxoo.com",
    "license": "OEEL-1",
    "depends": [
        "account_reports",
        "l10n_mx",
        "account_tax_cash_basis",
    ],
    "demo": [
        "demo/res_company_demo.xml",
        "demo/account_invoice_demo.xml",
        "demo/res_partner_demo.xml",
    ],
    "data": [
        "data/account_financial_report_data.xml",
        "data/country_data.xml",
        "views/res_country_view.xml",
        "views/res_partner_view.xml",
    ],
    "external_dependencies": {
        "python": ["cfdilib"],
    },
    'qweb': [
        'static/src/xml/account_report_backend.xml',
    ],
    "installable": True,
    "auto_install": False,
}
