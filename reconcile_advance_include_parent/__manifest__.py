# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Reconcile Advance Include Parent",
    "summary": "Call the original search to find each of the father's children's bills.",
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
        "base",
        "account",
        "gebesa_reconcile_advance",
        "invoice_apply_advance_invoice",

    ],
    "data": [
        "views/gebesa_reconcile_advance_view.xml",
        "views/account_invoice_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
