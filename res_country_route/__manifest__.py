# -*- coding: utf-8 -*-
{
    'name': "Rutas",

    'summary': """Delivery routes""",
    'author': 'Gebesa',
    'category': 'Sales',
    'version': '0.1',

    'depends': ['base', 'contacts'],

    'data': [
        'security/ir.model.access.csv',
        'views/res_country_route_view.xml',
        'views/res_country_state_views.xml',
    ],
    'demo': [

    ],
}
