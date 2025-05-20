# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Reporte Incidencias",
    "summary": "Reporte Incidencias",
    "version": "12.0.1.0.0",
    "category": "Uncategorized",
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
        "sale",
        "order_line_cancel",
    ],
    "data": [
        "views/reporte_incidencias.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
