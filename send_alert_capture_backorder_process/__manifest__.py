# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Alert Capture Backorder By Process',
    'summary': 'Send alert capture backorder by process',
    'version': '12.0.1.0.0',
    'category': 'Uncategorized',
    'website': 'https://odoo-community.org/',
    'author': '<Samuel Barron>, Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'base',
        'sale',
        'pivot_week_for_order'
    ],
    'data': [
        'data/ir_cron.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ]
}
