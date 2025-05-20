# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Sale order mrp boost',
    'summary': 'Sale order mrp boost',
    'version': '12.0.1.0.0',
    'category': 'Manufacturing',
    'website': 'https://odoo-community.org/',
    'author': '<AUTHOR(S)>, Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'base', 'mrp', 'sale', "mrp_gebesa",
        "report_tags", "sale_order_gebesa"
    ],
    'data': [
        'reports/report_tag_sol.xml',
        'views/sale_order.xml',
        'views/mrp_production.xml',
        'views/res_config_settings.xml',
        'views/mrp_segment_view.xml',
        'views/stock_picking_view.xml',
        'wizards/mrp_segment_add_production.xml',
        'wizards/mrp_production_segment_grouped_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ]
}
