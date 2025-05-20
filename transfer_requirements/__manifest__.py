# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Transfer Requirements",
    "summary": "Transfer Requirements",
    "version": "12.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://odoo-community.org/",
    "author": "Esther Cisneros, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "hr",
        'message_post_model',

    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        # "views/transfer_requirements.xml",
        "views/transfer_requirements2.xml",
        "views/trasnfer_requirements_secuence.xml",

    ],
    "demo": [

    ],
    "qweb": [

    ]
}
