import odoo

def migrate(cr, version):
    registry = odoo.registry(cr.dbname)
    from odoo.addons.sales_order_dealer.models.sale_order import update_table
    update_table(cr, registry)