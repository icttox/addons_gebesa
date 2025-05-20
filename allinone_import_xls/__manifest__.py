# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

{
    'name': 'AllInOne Import Purchase/Sale/Transfer/Reco from XLS',
    'version': '1.0',
    'category': 'tools',
    'summary': 'Purchase Import | Sale Import | Inventory Import | Picking Import | Stock Import | Excel Import | XLS Import | ALL IN ONE | Multiple Purchase Import',
    'description': """
Import data from XLS
========================
* Purchase Orders
* Sales Orders
* Internal Transfers
* Reconciliation Entries(Reco Entry-Inventory Adjustment)
""",
    'author': 'TidyWay',
    'website': 'http://www.tidyway.in',
    'depends': ['web', 'purchase', 'sale_stock', 'stock_warehouse_analytic_id'],
    'data': [
             'security/import_security.xml',
             'views/allinone_import_seq.xml',
             'wizard/allinone_message_view.xml',
             'views/allinone_import_view.xml',
           ],
    'price': 35,
    'currency': 'EUR',
    'installable': True,
    'license': 'OPL-1',
    'application': True,
    'auto_install': False,
    'images': ['images/cover.jpg'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
