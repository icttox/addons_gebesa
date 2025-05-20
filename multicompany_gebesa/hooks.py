# Copyright 2015-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging
from odoo import api, SUPERUSER_ID
_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    rule = env.ref('stock.stock_location_route_comp_rule')
    if not rule:
        return
    rule.write({
        'active': True,
        'domain_force': (
            "['|', ('company_ids', 'in', user.company_id.ids),"
            " ('company_ids', '=', False)]"
        ),
    })
    model = env['stock.location.route']
    table_name = model._fields['company_ids'].relation
    column1 = model._fields['company_ids'].column1
    column2 = model._fields['company_ids'].column2
    SQL = """
        INSERT INTO %s
        (%s, %s)
        SELECT id, company_id FROM %s WHERE company_id IS NOT NULL
    """ % (table_name, column1, column2, model._table)
    env.cr.execute(SQL)


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    rule = env.ref('stock.stock_location_route_comp_rule')
    if not rule:
        return
    rule.write({
        'domain_force': (
            " ['|', ('company_id', '=', user.company_id.id),"
            " ('company_id', '=', False)]"
        ),
    })
