# Copyright 2019, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "TMS Galbo Java Reports",
    'version': '1.0',
    'author': 'Cesar Barron, Gebesa',
    'category': 'Hidden',
    'license': 'AGPL-3',
    'summary': """Some useful reports for evaluation""",
    'description': """
TMS Galbo Java Reort
========================
Add several reports java type for evaluation Trucks, Drivers and Customers.
    """,
    'depends': ['flete_gebesa'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/tms_report.xml',
        'views/tms_search_template.xml',
        'views/tms_reports_view.xml'
    ],

    'installable': True,
    'application': False,
    'demo': [],
    'test': [],

}
