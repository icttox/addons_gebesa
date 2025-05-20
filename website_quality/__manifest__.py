# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Website Quality Alert',
    'summary': """Creates quality alert from website and notify the employee by e-mail""",
    'version': '12.0.1.0.0',
    'category': 'Website',
    'website': 'https://odoo-community.org/',
    'author': 'Samuel Barron, Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'base',
        'website',
        'management_system_gebesa',
        'web_widget_image_webcam',
    ],
    'data': [
        'views/templates.xml',
        'views/views.xml',
        'views/mail_template.xml',
        'views/quality_alert_view.xml',
        'views/mrp_workcenter_view.xml',
    ],
    'demo': [],
    'qweb': []
}
