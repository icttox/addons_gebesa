# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sales goals",
    "summary": "Sales goals.",
    "version": "12.0.1.0.0",
    "category": "Sales",
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
        "base", "sale",
        "sales_channel",
    ],
    "data": [
        "views/sale_goal.xml",
        "views/res_partner.xml",
        "security/security.xml",
        "security/ir.model.access.csv"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
