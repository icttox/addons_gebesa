# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP BOM Validate",
    "summary": "MRP BOM Validate",
    "version": "12.0.1.0.0",
    "category": "Personalized",
    "website": "https://odoo-community.org/",
    "author": "Aldo Nerio, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        'sale',
        'attachments_sale_order',
        "mrp",
        "mrp_cut_detail",
    ],
    "data": [
        "security/security.xml",
        "views/mrp_bom.xml"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
