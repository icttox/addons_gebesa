# -*- coding: utf-8 -*-
# © <2016> <César Barrón Bautista>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Gebesa MRP",
    "summary": "Modify MRP's default behavior to adapt it to Gebesa",
    "version": "12.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://odoo-community.org/",
    "author": "Cesar Barron, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base", "mrp",
        "l10n_mx_base",
        "mrp_cut_detail",
        "stock_warehouse_analytic_id",
        "sale_order_gebesa",
        "mrp_account",
        "product",
        "resource",
    ],
    "data": [
        "security/security.xml",
        "views/mrp_bom_view.xml",
        "views/sale_order_view.xml",
        "views/product_template_view.xml",
        "views/res_config_settings_view.xml",
        "reports/mrp_production_templates.xml",
        "reports/mrp_report_views_main.xml",
        "reports/mrp_production_template_geb.xml",
    ],
    "demo": [
        # "demo/res_partner_demo.xml",
    ],
    "qweb": [
        # "static/src/xml/module_name.xml",
    ]
}
