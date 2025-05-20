# Copyright 2023, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Website Production Load',
    'summary': 'Website Production Load',
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
        'reports/production_load_ticket.xml',
        'views/mrp_production_daily_load.xml',
        'views/product_template.xml',
        'views/website_templates.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ]
}
