# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models, fields
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_salesrep_id = fields.Many2one(
        'sale.salesrep',
        related='partner_id.salesrep_id',
        string='Partner REP',
        store=False
    )
    salesrep_ids = fields.Many2many(
        'sale.salesrep',
        related='partner_id.salesrep_ids',
        string='Partner REPS',
        store=False
    )
    salesrep_id = fields.Many2one(
        'sale.salesrep',
        string='REP',
    )

    sales_person_id = fields.Many2one(
        'res.users',
        string='Salesperson',
    )

    @api.onchange('salesrep_id')
    def onchange_salesrep_id(self):
        if self.salesrep_id and self.salesrep_id.team_id:
            self.team_id = self.salesrep_id.team_id.id
        elif self.partner_id and self.partner_id.team_id:
            self.team_id = self.partner_id.team_id.id
        else:
            self.team_id = False

    # @api.multi
    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     super().onchange_partner_id()
    #     if self.partner_id and self.partner_id.salesrep_id:
    #         self.salesrep_id = self.partner_id.salesrep_id.id

    @api.multi
    def write(self, vals):
        # Do not allow changing the partner_id when is an intercompany sale order
        if vals.get('partner_id', False):
            for order in self:
                if order.auto_purchase_order_id:
                    raise UserError(_('You cannot change the Customer of an intercompany Sale Order.'))
        # Do not allow changing the pricelist when is an intercompany sale order
        if vals.get('pricelist_id', False):
            for order in self:
                if order.auto_purchase_order_id:
                    raise UserError(_('You cannot change the Pricelist of an intercompany Sale Order.'))

        # Do not allow changing the invoice address when is an intercompany sale order
        if vals.get('partner_invoice_id', False):
            for order in self:
                if order.auto_purchase_order_id:
                    raise UserError(_('You cannot change the Invoice partner of an intercompany Sale Order.'))

        return super().write(vals)

    @api.multi
    def update_prices_to_po(self):
        # This method supouse to be used only troughout a server action
        sorders = self.filtered(lambda so: so.auto_purchase_order_id)
        lines = sorders.mapped('order_line').filtered(
            lambda li: li.auto_purchase_order_line_id)
        lines = lines.filtered(
            lambda li: li.price_unit != li.sudo().auto_purchase_order_line_id.price_unit)

        for line in lines:
            # target_comp = line.sudo().auto_purchase_order_line_id.order_id.company_id
            # intercompany_uid = target_comp.intercompany_user_id and\
            #     target_comp.intercompany_user_id.id or False
            # if not intercompany_uid:
            #     raise Warning(_(
            #         'Provide at least one user for inter company '
            #         'relation for % ') % target_comp.name)
            line.auto_purchase_order_line_id.sudo(
            ).price_unit = line.price_unit

    @api.multi
    def action_done(self):
        for sale in self:
            if sale.company_id.country_id != self.env.ref('base.mx'):
                continue
            for line in sale.order_line:
                if not line.tax_id:
                    raise UserError('Al menos una linea no tiene impuestos')

        res = super().action_done()

        self._cr.execute("""
            UPDATE purchase_order_line AS pol SET
                line_tag_number = sol.line_tag_number,
                reference_code = sol.reference_code
            FROM sale_order_line AS sol
            WHERE pol.sale_line_id = sol.id AND sol.order_id = %s
                AND (sol.line_tag_number IS NOT NULL
                OR sol.reference_code IS NOT NULL)
            """, (self.id,))

        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    auto_purchase_order_line_id = fields.Many2one(
        'purchase.order.line',
        string='Auto Purchase Order Line',
    )

    @api.multi
    def write(self, vals):
        # Do not allow changing the product_id when is an intercompany sale order
        if vals.get('product_id', False):
            for line in self:
                if line.auto_purchase_order_line_id:
                    raise UserError(_('You cannot change the product of an intercompany Sale Order.'))
        # Do not allow changing the qty when is an intercompany sale order
        if vals.get('product_uom_qty', False):
            for line in self:
                if line.auto_purchase_order_line_id:
                    raise UserError(_('You cannot change the quantity of an intercompany Sale Order.'))

        # Do not allow changing the price unit when is an intercompany sale order
        update_so_price_intercompany = self._context.get(
            'update_so_price_intercompany', False)
        if vals.get('price_unit', False) and not update_so_price_intercompany:
            for line in self:
                if line.auto_purchase_order_line_id:
                    raise UserError(_('You cannot change the price unit of an intercompany Sale Order.'))

        return super().write(vals)

    @api.model
    def create(self, vals_list):
        for line in self:
            if line.order_id.auto_purchase_order_id:
                raise UserError(_('You cannot add lines to an intercompany Sale Order.'))
        return super().create(vals_list)

    @api.multi
    def unlink(self):
        for line in self:
            if self.env.user.has_group('system_administrator.group_system_administrator_gebesa'):
                continue
            if line.auto_purchase_order_line_id:
                raise UserError(_('You cannot delete lines of an intercompany Sale Order.'))

        return super().unlink()
