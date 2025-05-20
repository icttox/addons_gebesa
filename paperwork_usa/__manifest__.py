# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Paperwork USA',
    'summary': 'Paperwork USA',
    'version': '12.0.1.0.0',
    'category': 'Sales',
    'website': 'https://odoo-community.org/',
    'author': 'Eduardo Lopez, Gebesa',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'base',
        'sale',
        'sale_order_gebesa',
        'report_xlsx',
        'mail',
        'mrp',
        'mrp_shipment',
        'report_tags',

    ],
    'data': [
        'reports/report_usa.xml',
        'views/sale_order_view.xml',
        'views/sale_order_line_view.xml',
        'views/sale_config.xml',
        'reports/bill_lading.xml',
        'views/mrp_shipment_line_view.xml',
        'views/mrp_shipment_view.xml',
        'views/res_partner.xml',
        'views/product_product.xml',
        'data/mail_template_data.xml',
        "data/report_paperformat.xml",
        'reports/packing_list.xml',
        'reports/packing_list_doc.xml',
        'reports/packing_list_report.xml',
        'reports/bill_lading_2.xml',
        'reports/bill_lading_2_doc.xml',
        'reports/bill_lading_2_report.xml',
        'reports/xls_reports.xml',
        'reports/tsca_format_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ]
}
