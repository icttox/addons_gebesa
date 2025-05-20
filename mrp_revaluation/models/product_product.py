# -*- coding: utf-8 -*-
# © <2016> <César Barron>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import _, api, models
from odoo.tools import float_is_zero
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _name = 'product.product'

    @api.model
    def do_change_standard_price2(self, rec_ids, new_price):
        move_obj = self.env['account.move']
        user_id = self.env.user
        company_id = user_id.company_id.id
        # import ipdb; ipdb.set_trace()
        for product in self.browse(rec_ids):
            diff = product.standard_price - new_price

            self._cr.execute("""
                WITH RECURSIVE actualiza_costo(group_id,id,code,num,ruta_id,ruta_code,company_id) AS(
                    SELECT
                        pp.id,
                        pp.id,
                        pp.default_code,
                        1.00,
                        CAST(pp.id AS TEXT),
                        pp.default_code,
                        %s
                    FROM product_product AS pp
                    WHERE pp.id = %s AND pp.active = True
                    UNION SELECT
                        ac.group_id,
                        pp.id,
                        pp.default_code,
                        ac.num * mbl.product_qty,
                        ac.ruta_id || CASE ac.ruta_id WHEN '/' THEN '' ELSE '/' END || pp.id,
                        ac.ruta_code || CASE ac.ruta_code WHEN '/' THEN '' ELSE '/' END || pp.default_code,
                        mb.company_id
                    FROM actualiza_costo AS ac
                    JOIN mrp_bom_line AS mbl ON ac.id = mbl.product_id
                    JOIN mrp_bom AS mb ON mbl.bom_id = mb.id AND mb.active = TRUE AND mb.company_id = ac.company_id
                    JOIN product_product AS pp ON mb.product_id = pp.id AND pp.active = TRUE
                )
                UPDATE ir_property AS ip
                    SET value_float = value_float + (T.sum * %s),
                        write_date = NOW(),
                        write_uid = %s
                FROM (SELECT id,code,sum(num),company_id FROM actualiza_costo
                        WHERE id IS NOT NULL GROUP BY id,code,company_id) AS T
                WHERE CONCAT('product.product,', T.id) = ip.res_id AND ip.name = 'standard_price' 
                    AND ip.fields_id = 2804 AND T.company_id = ip.company_id""",
                             (company_id, product.id, (diff * -1), user_id.id))

            self._cr.execute("""
                WITH RECURSIVE actualiza_costo(group_id,id,code,num,ruta_id,ruta_code,company_id) AS(
                    SELECT
                        pp.id,
                        pp.id,
                        pp.default_code,
                        1.00,
                        CAST(pp.id AS TEXT),
                        pp.default_code,
                        %s
                    FROM product_product AS pp
                    WHERE pp.id = %s AND pp.active = True
                    UNION SELECT
                        ac.group_id,
                        pp.id,
                        pp.default_code,
                        ac.num * mbl.product_qty,
                        ac.ruta_id || CASE ac.ruta_id WHEN '/' THEN '' ELSE '/' END || pp.id,
                        ac.ruta_code || CASE ac.ruta_code WHEN '/' THEN '' ELSE '/' END || pp.default_code,
                        mb.company_id
                    FROM actualiza_costo AS ac
                    JOIN mrp_bom_line AS mbl ON ac.id = mbl.product_id
                    JOIN mrp_bom AS mb ON mbl.bom_id = mb.id AND mb.active = TRUE AND mb.company_id = ac.company_id
                    JOIN product_product AS pp ON mb.product_id = pp.id AND pp.active = TRUE
                )
                INSERT INTO product_price_history(create_uid,create_date,product_id,company_id,datetime,cost,write_date,write_uid)
                SELECT
                    DISTINCT %s, NOW(), ac.id, ac.company_id, NOW(), ip.value_float, NOW(), %s
                FROM actualiza_costo AS ac
                LEFT JOIN ir_property AS ip ON CONCAT('product.product,', ac.id) = ip.res_id
                    AND ip.name = 'standard_price' AND ip.fields_id = 2804
                WHERE ac.id IS NOT NULL AND ip.company_id = ac.company_id """,
                             (company_id, product.id, user_id.id, user_id.id))

            self._cr.execute("""
                WITH RECURSIVE actualiza_costo(group_id,id,code,num,ruta_id,ruta_code,company_id) AS(
                    SELECT
                        pp.id,
                        pp.id,
                        pp.default_code,
                        1.00,
                        CAST(pp.id AS TEXT),
                        pp.default_code,
                        %s
                    FROM product_product AS pp
                    WHERE pp.id = %s AND pp.active = True
                    UNION SELECT
                        ac.group_id,
                        pp.id,
                        pp.default_code,
                        ac.num * mbl.product_qty,
                        ac.ruta_id || CASE ac.ruta_id WHEN '/' THEN '' ELSE '/' END || pp.id,
                        ac.ruta_code || CASE ac.ruta_code WHEN '/' THEN '' ELSE '/' END || pp.default_code,
                        mb.company_id
                    FROM actualiza_costo AS ac
                    JOIN mrp_bom_line AS mbl ON ac.id = mbl.product_id
                    JOIN mrp_bom AS mb ON mbl.bom_id = mb.id AND mb.active = TRUE  AND mb.company_id = ac.company_id
                    JOIN product_product AS pp ON mb.product_id = pp.id AND pp.active = TRUE
                )
                UPDATE product_product AS pp
                    SET write_date = NOW(),
                        write_uid = %s
                FROM (SELECT id,code,sum(num) FROM actualiza_costo WHERE id IS NOT NULL GROUP BY id,code) AS T
                WHERE pp.id = T.id""",
                             (company_id, product.id, user_id.id))

            self._cr.execute("""
                WITH RECURSIVE actualiza_costo(group_id,id,code,num,ruta_id,ruta_code,company_id) AS(
                    SELECT
                        pp.id,
                        pp.id,
                        pp.default_code,
                        1.00,
                        CAST(pp.id AS TEXT),
                        pp.default_code,
                        %s
                    FROM product_product AS pp
                    WHERE pp.id = %s AND pp.active = True
                    UNION SELECT
                        ac.group_id,
                        pp.id,
                        pp.default_code,
                        ac.num * mbl.product_qty,
                        ac.ruta_id || CASE ac.ruta_id WHEN '/' THEN '' ELSE '/' END || pp.id,
                        ac.ruta_code || CASE ac.ruta_code WHEN '/' THEN '' ELSE '/' END || pp.default_code,
                        mb.company_id
                    FROM actualiza_costo AS ac
                    JOIN mrp_bom_line AS mbl ON ac.id = mbl.product_id
                    JOIN mrp_bom AS mb ON mbl.bom_id = mb.id AND mb.active = TRUE AND mb.company_id = ac.company_id
                    JOIN product_product AS pp ON mb.product_id = pp.id AND pp.active = TRUE
                )
                SELECT
                    pp.default_code AS codigo,
                    pt.name AS producto,
                    sl.name AS locacion,
                    sw.account_analytic_id AS analitica,
                    ip.value_float AS costo,
                    aj.id AS diario,
                    CASE WHEN SUM(sq.quantity) * (ac.num * %s) > 0
                        THEN sl.account_id
                        ELSE aa.id END AS credit_account,
                    CASE WHEN SUM(sq.quantity) * (ac.num * %s) > 0
                        THEN aa.id
                        ELSE sl.account_id END AS debit_account,
                    SUM(sq.quantity) * (ac.num * %s) AS monto,
                    (ac.num * %s) AS cambio,
                    SUM(sq.quantity) AS existencia,
                    pp.id,sl.id
                FROM actualiza_costo AS ac
                JOIN product_product AS pp ON ac.id = pp.id
                LEFT JOIN ir_property AS ip ON CONCAT('product.product,', ac.id) = ip.res_id
                    AND ip.name = 'standard_price' AND ip.fields_id = 2804
                    AND ip.company_id = ac.company_id
                JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN ir_property AS ip4 ON CONCAT('product.template,', pt.id) = ip4.res_id
                    AND ip4.name = 'property_account_expense_id' AND ip4.fields_id = 4595
                    AND ip4.company_id = ac.company_id
                LEFT JOIN ir_property AS ip5 ON ip5.res_id IS NULL AND ac.company_id = ip5.company_id
                    AND ip5.name = 'property_account_expense_id' AND ip5.fields_id = 4595
                LEFT JOIN product_category AS pc ON pt.categ_id = pc.id
                LEFT JOIN ir_property AS ip2 ON CONCAT('product.category,', pc.id) = ip2.res_id
                    AND ip2.name = 'property_stock_journal' AND ip2.fields_id = 5379
                    AND ip2.company_id = ac.company_id
                LEFT JOIN ir_property AS ip3 ON ip3.res_id IS NULL AND ac.company_id = ip3.company_id
                    AND ip3.name = 'property_stock_journal' AND ip3.fields_id = 5379
                LEFT JOIN account_journal AS aj ON COALESCE(ip2.value_reference,ip3.value_reference) = CONCAT('account.journal,',aj.id)
                LEFT JOIN ir_property AS ip6 ON CONCAT('product.category,', pc.id) = ip6.res_id
                    AND ip6.name = 'property_account_expense_categ_id' AND ip6.fields_id = 4591
                    AND ip6.company_id = ac.company_id
                LEFT JOIN ir_property AS ip7 ON ip7.res_id IS NULL AND ac.company_id = ip7.company_id
                    AND ip7.name = 'property_account_expense_categ_id' AND ip7.fields_id = 4591
                LEFT JOIN account_account AS aa ON COALESCE(ip4.value_reference,ip5.value_reference,ip6.value_reference,ip7.value_reference) = CONCAT('account.account,',aa.id)
                JOIN stock_quant AS sq ON pp.id = sq.product_id AND ac.company_id = sq.company_id
                JOIN stock_location AS sl ON sq.location_id = sl.id AND sl.usage = 'internal' AND ac.company_id = sl.company_id
                JOIN stock_warehouse AS sw ON sl.stock_warehouse_id = sw.id AND ac.company_id = sw.company_id
                GROUP BY ac.num,pp.id,pt.id,sl.id,sw.id,aj.id,aa.id,ip.id
                ORDER BY pp.default_code,sl.name
                """, (company_id, product.id, diff, diff, diff, diff))
            if self._cr.rowcount:
                moves = self._cr.fetchall()
                for move in moves:
                    lines = [
                        (0, 0, {
                            'name': _('Standard Price changed [' + move[0] +
                                      '] ' + move[1] + ' for existing in ' +
                                      move[2]),
                            'account_id': move[7],
                            'debit': abs(move[8]),
                            'credit': 0,
                            'analytic_account_id': move[3],
                            'product_id': move[11],
                        }),
                        (0, 0, {
                            'name': _('Standard Price changed [' + move[0] +
                                      '] ' + move[1] + ' for existing in ' +
                                      move[2]),
                            'account_id': move[6],
                            'debit': 0,
                            'credit': abs(move[8]),
                            'analytic_account_id': move[3],
                            'product_id': move[11],
                        })]
                    move_vals = {
                        'journal_id': move[5],
                        'company_id': user_id.company_id.id,
                        'line_ids': lines,
                        'ref': ('Standard Price changed [' +
                                move[0] + '] ' + move[1] + ' for existing in ' +
                                move[2] + " cambio en valor: " + str(
                                    move[9] * -1) + ", existencia: " +
                                str(move[10])),

                        'location_id': move[12],
                    }
                    # import ipdb; ipdb.set_trace()
                    move_id = move_obj.create(move_vals)
                    move_id.post()

    @api.multi
    def do_change_standard_price(self, new_price, account_id):
        """ Changes the Standard Price of Product and creates an account move
        accordingly."""

        # super(ProductProduct, self).do_change_standard_price(
        #    cr, uid, ids, new_price, context=context)

        # Copiado completamente desde el fuente original
        # con la finalidad de poder manipular la poliza contable
        # Que genera por el cambio de costo estandard

        # comienza codigo original
        AccountMove = self.env['account.move']

        quant_locs = self.env['stock.quant'].sudo().read_group([('product_id', 'in', self.ids)], ['location_id'], ['location_id'])
        quant_loc_ids = [loc['location_id'][0] for loc in quant_locs]
        locations = self.env['stock.location'].search([('usage', '=', 'internal'), ('company_id', '=', self.env.user.company_id.id), ('id', 'in', quant_loc_ids)])

        product_accounts = {product.id: product.product_tmpl_id.get_product_accounts() for product in self}

        for location in locations:
            for product in self.with_context(location=location.id, compute_child=False).filtered(lambda r: r.valuation == 'real_time'):
                diff = product.standard_price - new_price
                if float_is_zero(diff, precision_rounding=product.currency_id.rounding):
                    raise UserError(_("No difference between standard price and new price!"))
                if not product_accounts[product.id].get('stock_valuation', False):
                    raise UserError(_('You don\'t have any stock valuation account defined on your product category. You must define one before processing this operation.'))
                qty_available = product.qty_available
                if qty_available:
                    # Accounting Entries
                    if diff * qty_available > 0:
                        debit_account_id = account_id
                        credit_account_id = product_accounts[product.id]['stock_valuation'].id
                    else:
                        debit_account_id = product_accounts[product.id]['stock_valuation'].id
                        credit_account_id = account_id

                    move_vals = {
                        'journal_id': product_accounts[product.id]['stock_journal'].id,
                        'company_id': location.company_id.id,
                        'line_ids': [(0, 0, {
                            'name': _('Standard Price changed  - %s') % (product.display_name),
                            'account_id': debit_account_id,
                            'debit': abs(diff * qty_available),
                            'credit': 0,
                            'product_id': product.id,
                        }), (0, 0, {
                            'name': _('Standard Price changed  - %s') % (product.display_name),
                            'account_id': credit_account_id,
                            'debit': 0,
                            'credit': abs(diff * qty_available),
                            'product_id': product.id,
                        })],
                    }
                    move = AccountMove.create(move_vals)
                    move.post()

        self.write({'standard_price': new_price})
        # Finaliza codigo original

        bom_line_obj = self.env['mrp.bom.line']
        product_obj = self.env['product.product']

        bom_line_ids = bom_line_obj.search([('product_id', '=', self.ids)])

        for bom_line in bom_line_ids:
            bom = bom_line.bom_id

            costo_tot = 0.00
            for bom_spec_line in bom.bom_line_ids:
                if bom_spec_line.product_id and bom_spec_line.product_id.id:
                    product = bom_spec_line.product_id
                    costo_tot += (
                        product.standard_price * bom_spec_line.product_qty)

            if bom.product_id and bom.product_id.id:
                if bom.product_id.standard_price != costo_tot:
                    bom.product_id.do_change_standard_price(costo_tot, account_id)
            elif bom.product_tmpl_id and bom.product_tmpl_id.id:
                if bom.product_tmpl_id.standard_price != costo_tot:
                    product_ids = product_obj.search([
                        ('product_tmpl_id', '=', bom.product_tmpl_id.id)])
                    product_ids.do_change_standard_price(costo_tot, account_id)
        return True


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _name = 'product.template'

    # def do_change_standard_price(self, cr, uid, ids, new_price, context=None):
    #     """ Changes the Standard Price of Product and creates an account move
    #     accordingly."""

    #     # super(ProductTemplate, self).do_change_standard_price(
    #     #    cr, uid, ids, new_price, context=context)

    #     # Copiado completamente desde el fuente original
    #     # con la finalidad de poder manipular la poliza contable
    #     # Que genera por el cambio de costo estandard

    #     # comienza codigo original
    #     location_obj = self.pool.get('stock.location')
    #     move_obj = self.pool.get('account.move')
    #     if context is None:
    #         context = {}
    #     user_company_id = self.pool.get(
    #         'res.users').browse(
    #             cr, uid, uid, context=context).company_id.id
    #     loc_ids = location_obj.search(
    #         cr, uid, [
    #             ('usage', '=', 'internal'),
    #             ('company_id', '=', user_company_id)])
    #     for rec_id in ids:
    #         datas = self.get_product_accounts(cr, uid, rec_id, context=context)
    #         for location in location_obj.browse(
    #                 cr, uid, loc_ids, context=context):
    #             c = context.copy()
    #             c.update({'location': location.id, 'compute_child': False})
    #             product = self.browse(cr, uid, rec_id, context=c)

    #             diff = product.standard_price - new_price
    #             # if not diff:
    #             #     raise UserError(
    #             #         _("No difference between standard price and new price!"))
    #             for prod_variant in product.product_variant_ids:
    #                 qty = prod_variant.qty_available
    #                 if qty:
    #                     # Accounting Entries
    #                     amount_diff = abs(diff * qty)
    #                     if diff * qty > 0:
    #                         debit_account_id = datas['expense'].id
    #                         credit_account_id = datas['stock_valuation'].id
    #                     else:
    #                         debit_account_id = datas['stock_valuation'].id
    #                         credit_account_id = datas['expense'].id

    #                     lines = [(0, 0, {'name': _(
    #                                      'Standard Price changed [' + product.default_code + '] ' + product.name + ' for existing in ' + location.name),
    #                                      'account_id': debit_account_id,
    #                                      'debit': amount_diff,
    #                                      'credit': 0,
    #                                      'analytic_account_id': location.account_analytic_id.id
    #                                      }),
    #                              (0, 0, {'name': _(
    #                                      'Standard Price changed [' + product.default_code + '] ' + product.name + ' for existing in ' + location.name),
    #                                      'account_id': credit_account_id,
    #                                      'debit': 0,
    #                                      'credit': amount_diff,
    #                                      'analytic_account_id': location.account_analytic_id.id
    #                                      })]
    #                     move_vals = {
    #                         'journal_id': datas['stock_journal'].id,
    #                         'company_id': location.company_id.id,
    #                         'line_ids': lines,
    #                         'ref': 'Standard Price changed [' + product.default_code + '] ' + product.name + ' for existing in ' + location.name,
    #                     }
    #                     move_id = move_obj.create(
    #                         cr, uid, move_vals, context=context)
    #                     move_obj.post(cr, uid, [move_id], context=context)
    #         self.write(cr, uid, rec_id, {'standard_price': new_price})
    #     # Finaliza codigo original

    #     bom_obj = self.pool.get('mrp.bom')
    #     prod_obj = self.pool.get('product.product')
    #     prod_tmpl_obj = self.pool.get('product.template')
    #     bom_line_obj = self.pool.get('mrp.bom.line')

    #     product_ids = prod_obj.search(
    #         cr, uid, [('product_tmpl_id', '=', ids)])

    #     bom_line_ids = bom_line_obj.search(
    #         cr, uid, [('product_id', '=', product_ids)])

    #     for bom_line in bom_line_ids:
    #         bomli = bom_line_obj.browse(cr, uid, bom_line, context=context)

    #         bom = bom_obj.browse(cr, uid, bomli.bom_id.id, context=context)

    #         costo_tot = 0.00
    #         for bom_spec_line in bom.bom_line_ids:
    #             bol = bom_line_obj.browse(
    #                 cr, uid, bom_spec_line.id, context=context)

    #             if bol.product_id and bol.product_id.id:
    #                 product = prod_obj.browse(
    #                     cr, uid, bol.product_id.id, context=context)
    #                 costo_tot += (
    #                     product.standard_price * bol.product_qty)

    #         if bom.product_id and bom.product_id.id:
    #             if bom.product_id.standard_price != costo_tot:
    #                 prod_obj.do_change_standard_price(
    #                     cr, uid, [bom.product_id.id], costo_tot, context)
    #         elif bom.product_tmpl_id and bom.product_tmpl_id.id:
    #             if bom.product_tmpl_id.standard_price != costo_tot:
    #                 prod_tmpl_obj.do_change_standard_price(
    #                     cr, uid, [bom.product_tmpl_id.id],
    #                     costo_tot, context)
    #     return True
