# -*- coding: utf-8 -*-
{
    'name': "Project Git Gitlab Gebesa",

    'summary': """
        Project Git Gitlab Gebesa""",

    'description': """
        Project Git Gitlab Gebesa
    """,

    'author': "Leslie Marquez, Gebesa",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'project_git_gitlab',
                'scrummer_git'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizards/commits_wizard.xml',
        'views/git_repository_view.xml',
        'views/git_user_view.xml',
        'views/project_task_view.xml',
        'views/git_branch_view.xml',
        'views/git_commit_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
