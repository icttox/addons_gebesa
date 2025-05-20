# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Picking Adjustement",
    "summary": "Adds the menu for Input and Output by Adjustment.",
    "version": "12.0.1.0.0",
    "category": "Stock",
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
        "stock",
        "sale",
        "stock_picking_invoice",
    ],
    "data": [
        "views/stock_picking_view.xml",
        "views/adjustment_input_view.xml",
        "views/adjustment_output_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
