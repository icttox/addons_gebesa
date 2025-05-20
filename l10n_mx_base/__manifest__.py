# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Odoo Mexican Localization",
    "summary": """
        Electronic invoicing, Electronic accounting, SAT validation
        tools exchange rate updated, DIOT reports  and more.
    """,
    "version": "12.0.4.0.0",
    "author": "Vauxoo, Gebesa",
    "category": "Accounting",
    "website": "http://www.vauxoo.com",
    "license": "OEEL-1",
    "depends": [
        "account_accountant",  # It doesn't make sense without full accounting.
        "base_vat",  # Mandatory feature to validate the VAT number
        "account_reports",
        "currency_rate_live",
        "account_cancel",
        "sale",
        "base_address_city",
        "document",  # Administer xml and PDF files need document module.
        "account_reports",
        "cfdi32",
        "invoice_refund_product_id",
        "l10n_mx_edi_extended",
        "l10n_mx_edi_customs",
    ],
    "demo": [
        "demo/res_config.xml",
        "demo/pac_vauxoo_demo.xml",
        "demo/res_partner_demo.xml",
        "demo/res_company_demo.xml",
        "demo/attachment_validate_sat_demo.xml",
        "demo/products_demo.xml",
        "demo/res_users_demo.xml",
        "demo/account_journal.xml",
        "demo/config_parameter_demo.xml",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "security/ir_rules.xml",
        "data/fiscal_position_data.xml",
        "data/res_banks_data.xml",
        "data/ir_cron_data.xml",
        "data/payment_method_data.xml",
        "data/action_server_data.xml",
        "views/account_journal_view.xml",
        "views/account_payment_view.xml",
        "views/account_report.xml",
        "views/account_view.xml",
        "views/bank_view.xml",
        "views/invoice_view.xml",
        "views/ir_sequence_view.xml",
        "views/l10n_mx_base_payment_report.xml",
        "views/l10n_mx_base_report.xml",
        "views/mail_invoice_template.xml",
        "views/payment_method_view.xml",
        "views/res_company_view.xml",
        "views/res_pac_view.xml",
        "views/res_partner_view.xml",
        "data/account_payment.xml",
    ],
    'external_dependencies': {
        'python': [
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
    # "post_init_hook": "post_init_hook",
    'images': [
        'images/main_screenshot.png'
    ],
    "qweb": [
    ],
}
