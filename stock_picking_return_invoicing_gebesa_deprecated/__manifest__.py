# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Refund Return Pickings",
    "summary": "Add an option to refund return pickings",
    "version": "11.0.1.0.0",
    "category": "Pickings",
    "website": "https://odoo-community.org/",
    "author": "Deysy Mascorro, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": False,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "stock",
        "sale_stock_picking_return_invoicing",
    ],
    "data": [
        "wizards/stock_return_picking_view.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
