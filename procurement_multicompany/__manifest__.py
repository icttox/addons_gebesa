# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Procurement Multicompany',
    'summary': 'Procurement Multicompany',
    'version': '12.0.0.1',
    'category': 'MRP',
    'website': 'https://odoo-community.org/',
    'author': 'Samuel Barron, Gebesa',
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
        'sale',
    ],
    'data': [
    ],
    'demo': [
    ],
    'qweb': [
    ]
}
