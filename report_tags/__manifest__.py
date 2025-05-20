# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Report tags",
    "summary": "Report tags",
    "version": "12.0.1.0.0",
    "category": "Product",
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
        "mrp_shipment",
        "mrp_segment",
        "report_barcode_inherit",
        "product_product_customer",
        # "system_administrator",
        "pivot_week_for_order",
        "purchase"
    ],
    "data": [
        "views/res_partner.xml",
        "views/sale_order.xml",
        "views/product_product_customer.xml",
        "data/report_paperformat.xml",
        "report/report_tag_layout.xml",
        "report/report_tag.xml",
        "report/report_tag_mrp_shipment.xml",
        "report/report_tag_mrp_shipment_2.xml",
        "report/report_tag_segment.xml",
        "report/report_tag_customizable.xml",
        "report/report_tag_customizable_segment.xml",
        "report/report_tag_customizable_order.xml",
        "report/report_tag_customer_code.xml",
        "report/report_tag_shipment_from_SO.xml",
        "report/report_tsca_title.xml",
        "report/report_tag_production_2x4.xml",
        "report/report_tag_2x4.xml",
        "report/report_tag_2x4_without_barcode.xml",
        "report/report_tag_production_2x4_without_barcode.xml",
        "report/report_tag_customer_code_so.xml",
        "report/report_tag_po.xml",
        "report/report_tag_winholt.xml",
        "report/report_tag_assembly_instructions.xml",
        "report/report_tag_mrp_shipment_3.xml",
        "report/report_customer_code_grainger_tag.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
