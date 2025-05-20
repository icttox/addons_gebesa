# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Medical Expenses",
    "summary": "Employee Medical Expense.",
    "version": "12.0.1.0.0",
    "category": "",
    "website": "https://odoo-community.org/",
    "author": "Leslie Marquez, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "hr",
        "account",
        "global_chatter",
    ],
    "data": [
        "views/hr_employee_medical_expense_secuence.xml",
        "security/hr_employee_expenses.xml",
        "security/ir.model.access.csv",
        "views/hr_employee_medical_expense_view.xml",
        "views/hr_employee_medical_expense_line_view.xml",
        "wizards/wizard_employee_import_expenses.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
