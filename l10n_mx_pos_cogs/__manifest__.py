# -*- coding: utf-8 -*-
# Copyright 2016 Vauxoo (Carlos <carlosecv74@gmail.com>,
#                        Osval Reyes <osval@vauxoo.com>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "POS with COGS moves",
    "version": "10.0.1.0.0",
    "author": "Vauxoo, Gebesa",
    "category": "Localization/Mexico",
    "website": "http://www.vauxoo.com/",
    "license": "OEEL-1",
    "depends": [
        "l10n_mx_base",
        "base_action_rule",
        "point_of_sale",
        "account_cancel",
    ],
    "demo": [
        'demo/product_demo.xml',
    ],
    "data": [
        'data/base_action_rule.xml',
        'views/pos_order_view.xml',
    ],
    "installable": True,
    "auto_install": False,
}
