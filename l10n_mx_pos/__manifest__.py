# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Mexican POS Management System",
    "version": "12.0.1.0.0",
    "author": "Vauxoo, Gebesa",
    "category": "Point of Sale",
    "website": "http://www.vauxoo.com",
    "license": "OEEL-1",
    "depends": [
        "l10n_mx_base",
        "point_of_sale",
        "document",
        "base_action_rule",
    ],
    "demo": [
    ],
    "data": [
        "data/action_server_data.xml",
        "views/point_of_sale_view.xml",
        "views/report_xml_session.xml",
    ],
    'external_dependencies': {
        'python': [
            'cfdilib',
            'num2words'
        ],
    },
    "installable": True,
    "auto_install": False,
    'images': [
        'images/main_screenshot.png'
    ],
}
