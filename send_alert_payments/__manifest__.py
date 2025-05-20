{
    "name": "Send Email Payments Of Yesterday",
    "summary": "Send Alert Payments Of Yesterday",
    "version": "12.0.1.0.0",
    "category": "Personalized",
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
        "account",
    ],
    "data": [
        'data/ir_cron.xml'
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
