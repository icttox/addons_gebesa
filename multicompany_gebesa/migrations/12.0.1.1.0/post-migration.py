# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("""
        INSERT INTO res_partner_sale_salesrep_rel(res_partner_id, sale_salesrep_id)
        SELECT id,salesrep_id FROM res_partner WHERE salesrep_id IS NOT NULL""")
