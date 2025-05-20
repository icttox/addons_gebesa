# -*- coding: utf-8 -*-
{
    'name': "EDI Retenciones",

    'summary': """
        Permite documentar la retención de impuestos efectuados y los pagos
        realizados a residentes en el extranjero.""",

    'description': """
         Cuando en la realización de una actividad económica estés obligado a
         expedir un CFDI por las retenciones de impuestos que efectúas, o bien
         por los pagos realizados, genera una factura de retenciones o
         información de pagos. Por ejemplo, en el caso de enajenación de
         acciones, dividendos o utilidades distribuidas, regalías por derechos
         de autor, pagos realizados a favor de residentes en el extranjero,
         intereses reales deducibles por créditos hipotecarios.
    """,

    'author': "Leslie Marquez, Gebesa",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail',
        'account',
        'l10n_mx_edi',
        'l10n_mx_edi_extended',
    ],

    # always loaded
    'data': [
        'data/l10n_mx_edi_retentions_secuence.xml',
        'data/l10n_mx_edi.retentions.type.csv',
        'data/l10n_mx_edi.taxpayer.type.csv',
        'data/l10n_mx_edi.dividend.or.profitableness.type.csv',
        'data/1.0/retention_cfdi.xml',
        'views/l10n_mx_edi_retentions_view.xml',
        'views/l10n_mx_edi_retentions_type_view.xml',
        'views/l10n_mx_edi_dividend_type_view.xml',
        'views/l10n_mx_edi_taxpayer_type_view.xml',
        'report/retentions_report.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
