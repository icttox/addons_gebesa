
{
    "name": "Test Log",
    "summary": "Test Log",
    "version": "12.0.1.0.0",
    "category": "Personalized",
    "website": "https://odoo-community.org/",
    "author": "Armando Robledo, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "account",
        "hr",
        "system_administrator",
        "message_post_model",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/test_log_view.xml",
        "report/registro_pruebas_view.xml"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
