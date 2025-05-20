# Copyright 2019, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Sale Order Line Validate",
    'version': '1.0',
    'author': 'Cesar Barron, Gebesa',
    'category': 'Sale',
    'license': 'AGPL-3',
    'summary': """Sale Order Line Validate""",
    'description': """
Sale Order Line Validate
========================
Allows validate sale order lines one by one.
    """,
    'depends': [
        'sale_stock',
        'sales_order_dealer',
        'order_line_cancel',

    ],
    'data': [
        'views/sale_order_views.xml',
        'data/ir_cron_data.xml',
    ],

    'installable': True,
    'application': False,
    'demo': [],
    'test': [],

}
