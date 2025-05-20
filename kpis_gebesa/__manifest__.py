# Copyright 2022, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Gebesa KPIs",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "category": "KPI reports",
    "summary": """KPI reports generator.""",
    "author": """Cesar Barron""",
    "depends": [
        # "payroll_gebesa",
        # "mrp_production_daily_load",
        "product_structure_gebesa",
        "account_accountant"],
    "data": [
        # "wizards/payroll_cost_production_views.xml",
        "views/account_analytic_account_views.xml",
    ],
    "demo": [],
    "test": [],
    "external_dependencies": {
        # "python": ["cryptography"],
    },
    "installable": True,
    "application": False,
}
