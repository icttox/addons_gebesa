# -*- coding: utf-8 -*-
{
    'name': "Help Desk Gebesa",

    'summary': """
        Help Desk Gebesa""",

    'description': """
        Help Desk Gebesa
    """,

    'author': "Leslie Marquez, Gebesa",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'maintenance', 'helpdesk', 'project', 'helpdesk_timesheet'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizards/create_task_view.xml',
        'wizards/make_maintenance_req_view.xml',
        'views/helpdesk_ticket.xml',
        'data/mail_ticket_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
