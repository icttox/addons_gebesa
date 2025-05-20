# -*- coding: utf-8 -*-
# Copyright 2017, Cesar Barron Bautista
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        for invoice in self:
            if invoice.company_id.country_id == self.env.ref('base.mx') or invoice.type != 'out_invoice':
                continue
            self._cr.execute("""
                SELECT name,default_code,id,COUNT(price_unit),COUNT(discount)
                FROM (
                    SELECT pt.name,pp.default_code,pp.id,ail.price_unit,ail.discount
                    FROM account_invoice_line AS ail
                    JOIN product_product AS pp ON ail.product_id = pp.id
                    JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                    WHERE ail.invoice_id = %s AND pt.type != 'service'
                    GROUP BY pp.id,pt.id,ail.price_unit,ail.discount
                ) AS agrupacion
                GROUP BY name,default_code,id HAVING COUNT(price_unit) > 1 OR COUNT(discount) > 1
            """ % (str(invoice.id)))
            if self._cr.rowcount:
                error = ""
                for product in self._cr.fetchall():
                    error += u"""El producto [%s]  %s se repite en la factura con diferente precio unitario o descuento
                    """ % (product[1], product[0])
                if error != "":
                    raise ValidationError(error)
        return super().action_invoice_open()
