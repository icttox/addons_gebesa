# Copyright 2023, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Website Work Orders',
    'summary': 'Website Work Orders',
    'version': '12.0.1.0.0',
    'category': 'Uncategorized',
    'website': 'https://erp.portalgebesa.com/web',
    'author': 'GEBESA, Samuel Barron',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'product',
        'mrp_production_daily_load',
    ],
    'data': [
        'views/website_templates.xml',
        'data/ir_cron.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ]
}
