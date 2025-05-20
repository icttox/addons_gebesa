# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Report Supplier Attachment",
    "summary": "Report Last Supplier Attachment",
    "version": "12.0.1.0.0",
    "category": "Product",
    "website": "https://odoo-community.org/",
    "author": "Armando Robledo, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base", "report_supplier_attachment"
    ],
    "data": [
        "report/last_supplier_attachment.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
