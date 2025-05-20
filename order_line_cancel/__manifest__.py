# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale Order Line Cancel',
    'summary': 'Sale Order Line Cancel',
    'version': '12.0.1.0.0',
    'category': 'Sale',
    'website': 'https://odoo-community.org/',
    'author': 'Samuel Barron, Gebesa',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'base',
        'sale_stock',
        'mrp',
        # 'system_administrator',
        'sale_order_gebesa',
        'backorder_pedido_ventas_simple',
        'backorder',
        'account_invoice_sale_data',
        'pivot_sale_channel',
        'contacts',
        'sale_order_everywhere',
    ],
    'data': [
        'views/sale_order.xml',
        'report/report_movements_generated_line_item.xml'
    ],
    'demo': [
    ],
    'qweb': [
    ]
}
