# -*- coding: utf-8 -*-
{
    'name': "hubspot_integration",

    'summary': """
     Hubspot key integration.""",

    'description': """
      HUBSPOT INTEGRATION
    """,

    'author': "Leslie Marquez, Gebesa",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'sale',
                'sale_order_gebesa',
                'crm'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/hubspot_integration_view.xml',
        'views/crm_lead_view.xml',
        'views/sale_order_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
