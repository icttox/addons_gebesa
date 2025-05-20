# -*- coding: utf-8 -*-
# Copyright 2016, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Website ecommerce and portal boilerplate for Gebesa',
    'summary': 'Customizations for gebesa',
    'version': '12.0.0.1.0.0',
    'category': 'Website',
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
        # 'website_portal_sale',
        'website_sale',
        'website',
        # 'website_quote',
        'kingfisher_pro',
        'global_product_view',
        'backorder_pedido_ventas_simple',
        "sale_stock",
        "project"
    ],
    'data': [
        'views/templates.xml',
        'views/kingfisher_theme.xml',
        'views/res_partner_view.xml',
        'views/product_product.xml',
        'views/sale_order_view.xml',
        'views/hubspot_id_view.xml',
        'views/res_config_settings_view.xml',
        "data/data.xml",
    ],
    'demo': [
        # 'demo/res_partner_demo.xml',
    ],
    'qweb': [
        # 'static/src/xml/module_name.xml',
    ]
}
