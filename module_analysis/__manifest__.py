# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Module Analysis",
    'summary': "Add analysis tools regarding installed modules",
    'description': "to know which installed modules comes from Odoo Core, OCA, or are",
    'author': 'Marco Esquivel, Gebesa',
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '12.0.1.0.3',
    'license': 'AGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/view_base_module_update.xml',
        'views/view_ir_module_author.xml',
        'views/view_ir_module_type.xml',
        'views/view_ir_module_type_rule.xml',
        'views/view_ir_module_module.xml',
        'views/view_ir_module_module_lines.xml',
        'data/ir_config_parameter.xml',
        'data/ir_module_type.xml',
        'data/ir_module_type_rule.xml',
    ],
    'external_dependencies': {
        'python': ['pygount'],
    },
    'post_init_hook': 'analyse_installed_modules',
    'installable': True,
}
