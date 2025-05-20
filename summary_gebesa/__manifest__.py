# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Summary Gebesa',
    'summary': 'summary for inventories and purchase orders',
    'version': '12.0.1.0.0',
    'category': 'Uncategorized',
    'website': 'https://odoo-community.org/',
    'author': 'Samuel Barron, GEBESA, Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'base',
        'product_structure_gebesa',
    ],
    'data': [
        'data/ir_cron_data.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/summary_date_dim.xml',
    ],
    'demo': [],
    'qweb': []
}
