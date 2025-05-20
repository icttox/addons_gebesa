# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sales Team Parent",
    "summary": "Sales Team Parent",
    "version": "12.0.1.0.0",
    "category": "Sales",
    "website": "https://odoo-community.org/",
    "author": "Deysy Mascorro, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "sale"
    ],
    "data": [
        "views/crm_team_view.xml"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
