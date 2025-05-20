# -*- coding: utf-8 -*-

import re
from odoo import _, api, models, fields
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pediment_number = fields.Char(
        string='Numero de pedimento',
        copy=False,
    )
    patente_aduanal = fields.Char(
        string='Patente aduanal',
        copy=False,
    )
    entry_date = fields.Datetime(
        string='Fecha de entrada',
        copy=False,
    )
    clave_aduanal = fields.Char(
        string='Clave aduanal',
        copy=False,
    )
    clave_pedimento = fields.Selection([
        ('IN', 'IN'),
        ('V1', 'V1'),
        ('AF', 'AF'),
        ('RT', 'RT')],
        string='Clave pedimento',
        track_visibility='always')
    double_export_invoice = fields.Boolean(
        string='Debo facturar el resto de los productos que no son de exportacion de retorno',
    )

    @api.onchange('pediment_number')
    def _onchange_pediment_number(self):
        pattern = re.compile("([0-9]{7}$)")
        if self.pediment_number:
            if not pattern.match(self.pediment_number):
                self.pediment_number = ''
                warning_mess = {
                    'title': _('Validation Error'),
                    'message': _('Please enter valid Petiment number.')
                }
                return {'warning': warning_mess}
        return {}

    @api.onchange('patente_aduanal')
    def _onchange_patente_aduanal(self):
        pattern = re.compile("([0-9]{4}$)")
        if self.patente_aduanal:
            if not pattern.match(self.patente_aduanal):
                self.patente_aduanal = ''
                warning_mess = {
                    'title': _('Validation Error'),
                    'message': _('Please enter valid Customs Patent.')
                }
                return {'warning': warning_mess}
        return {}

    @api.onchange('clave_aduanal')
    def _onchange_clave_aduanal(self):
        pattern = re.compile("([0-9]{3}$)")
        if self.clave_aduanal:
            if not pattern.match(self.clave_aduanal):
                self.clave_aduanal = ''
                warning_mess = {
                    'title': _('Validation Error'),
                    'message': _('Please enter valid Customs code.')
                }
                return {'warning': warning_mess}
        return {}

    @api.multi
    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res['patente_aduanal'] = self.patente_aduanal or ''
        res['clave_aduanal'] = self.clave_aduanal or ''
        res['entry_date'] = self.entry_date
        res['petition_number'] = self.pediment_number or ''
        # if self.partner_id.country_id.code != 'MX':
        #     res['clave_pedimento'] = 'RT'
        #     self.clave_pedimento = 'RT'
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def invoice_line_create_vals(self, invoice_id, qty):
        uom_obj = self.env['uom.uom']
        product_obj = self.env['product.product']
        factor_obj = self.env['product.uom.factor']
        partidas_obj = self.env['l10n.mx.immex.partida']
        if self.order_id.partner_id.country_id.code != 'MX' and \
                self.order_id.partner_id.omitir_rt is not True:
            immex_type_count = self._context.get('immex_type_count', 0)
            if immex_type_count > 0:
                company_id = self.env.user.company_id.id
                self._cr.execute("""
                    WITH RECURSIVE bom_detail(product_id,immex_type_id,qty,company_id,exceptions_apply,download_immex,lv) AS(
                        SELECT
                            pp.id,
                            pt.immex_type_id,
                            %s,
                            %s,
                            ipt.download_exceptions_apply,
                            pt.apply_download_immex,
                            LPAD(CAST(ROW_NUMBER() OVER (ORDER BY pp.id) AS TEXT), 3, '0')
                        FROM product_product AS pp
                        JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                        LEFT JOIN l10n_mx_immex_partida_type AS ipt ON pt.immex_type_id = ipt.id
                        WHERE pp.id = %s
                        UNION SELECT
                            pp.id,
                            pt.immex_type_id,
                            ROUND(bd.qty * ((mb.product_qty * mbl.product_qty) / mb.product_qty),6),
                            bd.company_id,
                            ipt.download_exceptions_apply,
                            bd.download_immex,
                            CONCAT(bd.lv, '.', LPAD(CAST(ROW_NUMBER() OVER (ORDER BY bd.product_id,mbl.id) AS TEXT), 3, '0'))
                        FROM bom_detail AS bd
                        JOIN mrp_bom AS mb on bd.product_id = mb.product_id
                            AND bd.company_id = mb.company_id AND mb.active IS True
                        LEFT JOIN mrp_bom_line AS mbl on mb.id = mbl.bom_id
                        LEFT JOIN product_product AS pp ON mbl.product_id = pp.id
                        JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                        LEFT JOIN l10n_mx_immex_partida_type AS ipt ON pt.immex_type_id = ipt.id)
                    SELECT product_id,SUM(qty),immex_type_id FROM bom_detail
                    WHERE immex_type_id IS NOT NULL
                        AND (exceptions_apply IS NOT TRUE OR (exceptions_apply IS TRUE AND download_immex IS TRUE))
                    GROUP BY product_id,immex_type_id""", (
                    [qty, company_id, self.product_id.id]))
                products_immex = self._cr.fetchall()
                if not products_immex:
                    qty = 0
                else:
                    invoiced = False
                    for product in products_immex:
                        partidas = partidas_obj.search([
                            ('immex_type_id', '=', product[2]),
                            ('amount', '>', 0.00)])
                        partidas = partidas.filtered(
                            lambda x: x.porcentaje_desperdicio < (
                                (100 * x.amount) / float(x.cantidad_udm_comercial)))
                        if not partidas:
                            continue
                        product_id = product_obj.browse([product[0]])
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
                            #     invoiced = True
                            invoiced = True

                    if not invoiced:
                        qty = 0
        res = super().invoice_line_create_vals(invoice_id, qty)
        if res == []:
            res.append({'immex_not_invoce': True})
        return res
