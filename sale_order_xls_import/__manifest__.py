# Copyright 2019, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Sale Order Line Import",
    'version': '1.0',
    'author': 'Cesar Barron, Gebesa',
    'category': 'Sale',
    'license': 'AGPL-3',
    'summary': """Sale Order Line Import""",
    'description': """
Sale Order Line Import
========================
Allows import sale order lines into a created sale order.
    """,
    'depends': ['sale', 'account_invoice_sale_data', 'pivot_week_for_order', 'paperwork_usa'],
    'data': [
        "security/security.xml",
        'wizards/sale_order_import_views.xml',
        'wizards/sale_order_line_update_price_wizard.xml',
        'wizards/set_reposition_data_view.xml',
        'views/sale_order_view.xml',
        "views/sale_order_line.xml",
        'views/sale_order_line_view.xml',
    ],

    'installable': True,
    'application': False,
    'demo': [],
    'test': [],

}
