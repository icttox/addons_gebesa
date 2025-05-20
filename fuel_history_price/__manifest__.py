# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Fuel History Price",
    "summary": "Historical Fuel Price",
    "version": "12.0.1.0.0",
    "category": "Generic Modules",
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
        "tms"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/fuel_history_price.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
