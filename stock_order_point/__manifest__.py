# Copyright 2023, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Inventory order point',
    'summary': 'Inventory order point in weeks',
    'version': '1.0.0',
    'category': 'Warehouse',
    'website': 'https://odoo-community.org/',
    'author': 'Samuel Barron, Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'base',
        'stock',
    ],
    'data': [
        "data/ir_cron_data.xml",
        "views/stock_warehouse_orderpoint.xml"
    ],
    'demo': [
    ],
    'qweb': [
    ]
}
