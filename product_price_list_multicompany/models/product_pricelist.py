# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


# 2 espacios despues de importar y comienzo de clase
class ProductPricelist(models.Model):
    # La clase va con mayuscula la primera palabra
    _inherit = 'product.pricelist'
    # nombre de modelo igual ala tabla de la bd

    def propagate_pricelist_to_companies(self):
        partners = self.env['res.company'].sudo().search([]).mapped('partner_id')

        user = self.env.ref('base.user_admin')
        pricelists = partners.sudo(user.id).mapped('property_product_pricelist')
        for plist in pricelists:
            plist.pricelist_propagate()

        return True

    @api.multi
    def pricelist_propagate(self):

        # partner_obj = self.env['res.partner']
        company_obj = self.env['res.company']
        # product_obj = self.env['product.product']
        # product_supplier_info_obj = self.env['product.supplierinfo']
        supplier = self.company_id.partner_id
        self._cr.execute(
            """
                SELECT rp.id,rc.id FROM res_partner AS rp
                JOIN ir_property AS ip ON CONCAT('res.partner,', rp.id) = ip.res_id
                    AND ip.name = 'property_product_pricelist' AND ip.company_id = %s
                JOIN product_pricelist AS pp ON
                    ip.value_reference = CONCAT('product.pricelist,', pp.id)
                JOIN res_company AS rc ON rp.id = rc.partner_id
                WHERE rp.customer IS TRUE
                    AND pp.id = %s
            """, ([self.company_id.id, self.id]))
        partners = self._cr.fetchall()
        for client in partners:
            company = company_obj.sudo().browse([client[1]])
            if company:
                user = company.intercompany_user_id.id
                # for dato in self.item_ids:
                #     producto = product_obj.sudo(user).with_context(
                #         active_test=False).search([
                #             ('id', '=', dato.product_id.id)])
                #     if producto:
                #         supplierinfo = product_supplier_info_obj.sudo(user).search([
                #             ('product_id', '=', producto.id),
                #             ('name', '=', supplier.id),
                #             ('product_tmpl_id', '=', producto.product_tmpl_id.id),
                #             ('min_qty', '=', dato.min_quantity)], limit=1)
                #         if supplierinfo:
                #             supplierinfo.price = dato.fixed_price
                #         else:
                #             product_supplier_info_obj.sudo(user).create({
                #                 'name': supplier.id,
                #                 'product_id': producto.id,
                #                 'min_qty': dato.min_quantity,
                #                 'currency_id': self.currency_id.id,
                #                 'product_tmpl_id': producto.product_tmpl_id.id,
                #                 'price': dato.fixed_price,
                #                 'delay': 1
                #             })
                self._cr.execute(
                    """
                        DELETE FROM product_supplierinfo WHERE name = %s
                            AND company_id = %s
                            AND product_id IN (
                                SELECT product_id FROM product_pricelist_item
                                WHERE pricelist_id = %s)
                    """, ([supplier.id, company.id, self.id]))
                self._cr.execute(
                    """
                        INSERT INTO product_supplierinfo(create_uid,create_date,product_id,
                            sequence,company_id,write_uid,currency_id,delay,write_date,price,
                            min_qty,product_tmpl_id,name,preferred_supplier)
                        SELECT %s,NOW(),pp.id,1,%s,%s,ppr.currency_id,1,NOW(),
                            ppi.fixed_price,ppi.min_quantity,pp.product_tmpl_id,%s,False
                        FROM product_pricelist AS ppr
                        JOIN product_pricelist_item AS ppi ON ppr.id = ppi.pricelist_id
                        JOIN product_product AS pp ON ppi.product_id = pp.id
                        WHERE ppr.id = %s
                    """, ([user, company.id, user, supplier.id, self.id]))
