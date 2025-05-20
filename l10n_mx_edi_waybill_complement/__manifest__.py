# -*- coding: utf-8 -*-
{
    'name': "Waybill Complement",

    'summary': """
        L10n Mx Edi Waybill Complement""",

    'description': """
        L10n Mx Edi Waybill Complement
    """,

    'author': "Leslie Marquez, Gebesa",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'tms',
        # 'account_invoice_gebesa',
        'flete_gebesa',
        'l10n_mx_edi_extended'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/l10n_mx_wbl_transport_view.xml',
        'views/l10n_mx_wbl_stations_view.xml',
        'views/l10n_mx_wbl_type_station_view.xml',
        'views/l10n_mx_wbl_unit_weight_view.xml',
        'views/l10n_mx_wbl_dangerous_material_view.xml',
        'views/l10n_mx_wbl_packing_type_view.xml',
        'views/l10n_mx_wbl_permit_type_view.xml',
        'views/l10n_mx_wbl_autotransport_conf_view.xml',
        'views/l10n_mx_wbl_trailer_type_view.xml',
        'views/l10n_mx_wbl_maritime_conf_view.xml',
        'views/l10n_mx_wbl_load_type_view.xml',
        'views/l10n_mx_wbl_maritime_containers_view.xml',
        'views/l10n_mx_wbl_shipping_agent_consignee_view.xml',
        'views/l10n_mx_wbl_service_type_view.xml',
        'views/l10n_mx_wbl_stcc_products_services_view.xml',
        'views/l10n_mx_wbl_car_type_view.xml',
        'views/l10n_mx_wbl_container_type_view.xml',
        'views/l10n_mx_wbl_products_services_view.xml',
        'views/l10n_mx_wbl_figure_transport_view.xml',
        'views/l10n_mx_wbl_transport_part_view.xml',
        'views/tms_travel_view.xml',
        'views/res_company_view.xml',
        'views/fleet_vehicle_view.xml',
        'views/tms_transportable_view.xml',
        'views/res_partner_view.xml',
        'views/account_invoice_view.xml',
        'data/l10n.mx.wbl.transport.csv',
        'data/l10n.mx.wbl.stations.csv',
        'data/l10n.mx.wbl.type.station.csv',
        'data/l10n.mx.wbl.unit.weight.csv',
        'data/l10n.mx.wbl.dangerous.material.csv',
        'data/l10n.mx.wbl.packing.type.csv',
        'data/l10n.mx.wbl.permit.type.csv',
        'data/l10n.mx.wbl.autotransport.conf.csv',
        'data/l10n.mx.wbl.trailer.type.csv',
        'data/l10n.mx.wbl.maritime.conf.csv',
        'data/l10n.mx.wbl.maritime.containers.csv',
        'data/l10n.mx.wbl.load.type.csv',
        'data/l10n.mx.wbl.shipping.agent.consignee.csv',
        'data/l10n.mx.wbl.car.type.csv',
        'data/l10n.mx.wbl.service.type.csv',
        'data/l10n.mx.wbl.container.type.csv',
        'data/l10n.mx.wbl.products.services.csv',
        'data/l10n.mx.wbl.stcc.products.services.csv',
        'data/l10n.mx.wbl.figure.transport.csv',
        'data/l10n.mx.wbl.transport.part.csv',
        'data/2.0/waybill20.xml',
        'data/3.0/waybill30.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
