# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP PLM GEBESA",
    "summary": "MRP PLM GEBESA",
    "version": "12.0.1.0.0",
    "category": "MRP",
    "website": "https://odoo-community.org/",
    "author": "Aldo Nerio, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        'base', 'sale',
        'attachments_sale_order',
        "cfdi32",
        "invoice_refund_validate",
        "product",
        "stock",
        "mrp",
        "mrp_plm",
        "product_variant_default_code",
        "account",
        "report_tags",
    ],
    "data": [
        'data/ir_cron.xml',
        "security/security.xml",
        'security/ir.model.access.csv',
        # 'data/mail_template_data.xml',
        'data/new_task_mail_template.xml',
        'data/email_template_finish_task.xml',
        "views/template_sequence.xml",
        "wizards/wizard_plm.xml",
        "views/product_template.xml",
        "views/project_task.xml",
        "reports/etiqueta_codigo_barras.xml",
        "views/project_task_stage_hist_view.xml",
        "views/project_task_user_hist_view.xml",
        'data/config_parameter.xml',
        'views/mrp_eco_view.xml',
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
