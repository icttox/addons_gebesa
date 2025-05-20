# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def create_invoices(self):
        partidas_obj = self.env['l10n.mx.immex.partida']
        uom_obj = self.env['uom.uom']
        product_obj = self.env['product.product']
        factor_obj = self.env['product.uom.factor']
        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        company_id = self.env.user.company_id.id
        ctx = self._context.copy()
        for order in sale_orders:
            if order.partner_id.country_id.code != 'MX' and \
                    order.partner_id.omitir_rt is not True:
                self._cr.execute("""
                    WITH RECURSIVE bom_detail(order_line_id,product_id,immex_type_id,qty,company_id,exceptions_apply,download_immex,lv) AS(
                        SELECT
                            sol.id,
                            pp.id,
                            pt.immex_type_id,
                            sol.qty_to_invoice,
                            %s,
                            ipt.download_exceptions_apply,
                            pt.apply_download_immex,
                            LPAD(CAST(ROW_NUMBER() OVER (ORDER BY sol.id) AS TEXT), 3, '0')
                        FROM sale_order so
                        JOIN sale_order_line sol ON so.id = sol.order_id
                        JOIN product_product AS pp ON sol.product_id = pp.id
                        JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                        LEFT JOIN l10n_mx_immex_partida_type AS ipt ON pt.immex_type_id = ipt.id
                        WHERE so.id = %s AND sol.qty_to_invoice > 0
                        UNION SELECT
                            bd.order_line_id,
                            pp.id,
                            pt.immex_type_id,
                            ROUND(bd.qty * ((mb.product_qty * mbl.product_qty) / mb.product_qty),6),
                            bd.company_id,
                            ipt.download_exceptions_apply,
                            bd.download_immex,
                            CONCAT(bd.lv, '.', LPAD(CAST(ROW_NUMBER() OVER (ORDER BY bd.order_line_id,mbl.id) AS TEXT), 3, '0'))
                        FROM bom_detail AS bd
                        JOIN mrp_bom AS mb on bd.product_id = mb.product_id
                            AND bd.company_id = mb.company_id AND mb.active IS True
                        LEFT JOIN mrp_bom_line AS mbl on mb.id = mbl.bom_id
                        LEFT JOIN product_product AS pp ON mbl.product_id = pp.id
                        JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                        LEFT JOIN l10n_mx_immex_partida_type AS ipt ON pt.immex_type_id = ipt.id)
                    SELECT product_id,SUM(qty),immex_type_id,order_line_id FROM bom_detail
                    WHERE immex_type_id IS NOT NULL
                        AND (exceptions_apply IS NOT TRUE OR (exceptions_apply IS TRUE AND download_immex IS TRUE))
                    GROUP BY order_line_id,product_id,immex_type_id""", (
                    [company_id, order.id]))
                products = self._cr.fetchall()
                # import ipdb; ipdb.set_trace()
                delete_product = []
                for product in products:
                    partidas = partidas_obj.search([
                        ('immex_type_id', '=', product[2]),
                        ('amount', '>', 0.00)])
                    partidas = partidas.filtered(
                        lambda x: x.porcentaje_desperdicio < (
                            (100 * x.amount) / float(x.cantidad_udm_comercial)))
                    if not partidas:
                        delete_product.append(product)
                    else:
                        product_id = product_obj.browse([product[0]])
                        delete = True
                        for partida in partidas:
                            uom_id = uom_obj.search([
                                ('fiscal_code', '=', partida.udm_comercial)])
                            factor_id = factor_obj.search([
                                ('unmed_origin_id', '=', product_id.uom_id.id),
                                ('unmed_dest_id', 'in', uom_id.ids)])
                            if not factor_id:
                                raise UserError(_('No se necontro un factor de \
                                    conversion para el producto %s de %s a %s') % (
                                    product_id.default_code,
                                    product_id.uom_id.name, uom_id.name))

                            # detail = factor_id.mapped('details_ids').filtered(
                            #     lambda r: r.product_id.id == product_id.id)

                            # if detail.factor <= partida.amount:
                            #     delete = False
                            delete = False
                        if delete:
                            delete_product.append(product)

                for delete in delete_product:
                    products.remove(delete)
                ctx.update({'immex_type_count': len(products)})
                if products and not order.double_export_invoice:
                    raise UserError(
                        'Este pedido se facturara parcial mente, Porfavor confirmar de enterado')
        return super(SaleAdvancePaymentInv, self.with_context(ctx)).create_invoices()
