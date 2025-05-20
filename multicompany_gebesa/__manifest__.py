# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Multicompany gebesa",
    "summary": "Multicompany gebesa",
    "version": "12.0.1.1.0",
    "category": "Personalization",
    "website": "https://odoo-community.org/",
    "author": "Samuel Barron, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "mrp",
        "stock",
        "inter_company_rules",
        "res_company_manufacturer",
    ],
    "data": [
        "security/security.xml",
        "views/res_company.xml",
        "views/purchase_order.xml",
        "views/stock_location_route.xml",
        "views/res_partner.xml",
        "views/sales_order.xml",
        "views/sale_salesrep.xml",
        "views/res_config_settings.xml",
        "wizards/update_price_po_so_wizard.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
    ],
    "qweb": [
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
