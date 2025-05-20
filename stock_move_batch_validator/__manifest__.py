# -*- coding: utf-8 -*-
# Copyright 2017, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Stock Moves batch validator by id',
    'summary': 'Validate stock moves given a set of ids',
    'version': '12.0.1.0.0',
    'category': 'Uncategorized',
    'website': 'https://odoo-community.org/',
    'author': 'Cesar Barron, Gebesa',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'base',
        'stock',
        'mrp_segment',
    ],
    'data': [
        'security/security_mrp_production_all_processes.xml',
        'wizards/batch_stock_moves_ids_view.xml',
        'wizards/batch_mrp_production_names_view.xml',
        'wizards/batch_mrp_production_names_transfer_view.xml',
        'wizards/batch_mrp_production_names_ppt.xml',
        'wizards/mrp_production_all_processes.xml',
        'views/mrp_segment.xml',
        'data/ir_cron_data.xml',
    ],
    'demo': [
        # 'demo/res_partner_demo.xml',
    ],
    'qweb': [
        # 'static/src/xml/module_name.xml',
    ]
}
