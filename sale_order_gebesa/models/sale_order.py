# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo.tools import config

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_shipping_id = fields.Many2one(
        'res.partner',
        string='Delivery Address',
        readonly=True,
        required=False,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},
        help="Delivery address for current sales order."
    )

    notify_approval = fields.Char(
        string='Notify approval',
        size=100,
    )

    date_delivery = fields.Date(
        string='Date delivery',
        default=fields.Date.today,
    )

    date_reception = fields.Date(
        string='Date reception',
    )

    total_net_sale = fields.Float(
        string='Total net sale',
        digits=dp.get_precision('Account'),
        # compute='_compute_profit_margin',
        store=True
    )

    perc_freight = fields.Float(
        string='Freight percentage',
        digits=dp.get_precision('Account'),
    )

    total_freight = fields.Float(
        string='Total Freight',
        digits=dp.get_precision('Account'),
        # compute='_compute_profit_margin',
        store=True
    )

    perc_installation = fields.Float(
        string='installation percentage',
        digits=dp.get_precision('Account'),
    )

    freight_expense = fields.Float(
        string='Actual Freight Expense',
    )

    total_installation = fields.Float(
        string='Total installation',
        digits=dp.get_precision('Account'),
        # compute='_compute_profit_margin',
        store=True
    )

    profit_margin = fields.Float(
        string='Profit margin',
        digits=dp.get_precision('Account'),
        # compute='_compute_profit_margin',
        store=True
    )

    not_be_billed = fields.Boolean(
        string='not be billed',
    )

    no_facturar = fields.Boolean(
        string='No Facturar',
    )

    manufacture = fields.Selection(
        [('special', 'Special'),
            ('line', 'Line'),
            ('replenishment', 'Replenishment'),
            ('semi_special', 'Semi special')],
        string="Manufacture",
    )

    executive = fields.Char(
        string='Executive',
        size=100,
    )

    respo_reple = fields.Char(
        string='Responsible of replenishment',
        size=200,
    )

    priority = fields.Selection(
        [('high', 'High'), ('replenishment', 'Replenishment'),
         ('express', 'Express'), ('sample', 'Sample'),
         ('quick_ship', 'Quick Ship')],
        'Manufacturing priority',)

    complement_saleorder_id = fields.Many2one(
        'sale.order',
        string='In complement:',
        help='Displays a list of sales orders',
    )

    manufacturing_observations = fields.Text(
        string='Observations Manufacturing',
    )

    replenishing_motif = fields.Text(
        string='Reason for the replenishment',
    )

    credit_status = fields.Selection(
        [('normal', 'Normal'),
         ('suspended', 'Suspended for Collection'),
         ('conditioned', 'Conditioned')],
        'Credit status',)

    credit_note = fields.Text(
        string='Note Credit and Collections',
    )

    date_production = fields.Date(
        string='Date of Production Termination',
    )

    approve = fields.Selection(
        [('approved', 'Approved'),
         ('suggested', 'Suggested for Approval'),
         ('not_approved', 'Not Approved')],
        default='not_approved',
        string='Approve Status',
        store=True,
        copy=False,
    )

    total_cost = fields.Float(
        string='Total cost',
        # compute='_compute_profit_margin',
        store=True
    )

    sale_picking_adm = fields.Boolean(
        string='Admin Sale Picking',
    )

    webiste_operator = fields.Boolean(
        string='Captured by Operator',
    )

    date_suggested = fields.Datetime(
        string='Suggestion Date Approval',
        copy=False,
        help='Suggestion Date Approval.')

    date_approved = fields.Datetime(
        string='Credit Release Date',
        copy=False,
        help='Credit Release Date.')

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The order name must be unique"),
    ]

    def _amount_all(self):
        if isinstance(self.id, int):
            if self.company_id.is_manufacturer and self.approve == 'approved':
                self.write({'approve': 'suggested'})
        return super()._amount_all()

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.webiste_operator = False
        self.notify_approval = False
        if self.partner_id:
            self.webiste_operator = True
        if self.partner_id.notify_approval:
            self.notify_approval = self.partner_id.notify_approval

    # @api.depends('order_line.net_sale')
    @api.multi
    def calculate_profit_margin(self):
        for order in self:
            global_cost = 0.0
            global_net_sale = 0.0
            global_freight = 0.0
            global_installa = 0.0
            global_profit_margin = 0.0
            currency = order.company_id.currency_id
            if self.env.context.get('recalculate_line', False):
                order.order_line._compute_purchase_price_geb()
                order.order_line._compute_profit_margin()
            for line in order.order_line:
                global_cost += line.standard_cost
                global_net_sale += line.net_sale
                global_freight += line.freight_amount
                global_installa += line.installation_amount

            if global_net_sale > 0.000000:
                # global_total_pm = currency.compute(
                #     global_cost, order.pricelist_id.currency_id)
                global_total_pm = currency._convert(
                    global_cost, order.pricelist_id.currency_id, order.company_id, fields.Date.today())
                global_profit_margin = (
                    1 - (global_total_pm) / global_net_sale)
                global_profit_margin = global_profit_margin * 100

            order.total_cost = global_cost
            order.total_net_sale = global_net_sale
            order.total_freight = global_freight
            order.total_installation = global_installa
            order.profit_margin = global_profit_margin

    @api.multi
    def decrease_price_percent(self, percent_decrease):

        its_us = self.env.user.has_group(
            'system_administrator.group_system_administrator_gebesa')
        if not its_us:
            return

        for order in self:
            order.state = 'sale'
            for line in order.order_line:
                line.price_unit = (line.price_unit * (1.00 - (percent_decrease / 100)))
            order.state = 'done'

    @api.multi
    def increase_price_percent(self, absolute_percent):

        its_us = self.env.user.has_group(
            'system_administrator.group_system_administrator_gebesa')
        if not its_us:
            return

        for order in self:
            order.state = 'sale'
            for line in order.order_line:
                line.price_unit = (line.price_unit * (1 + (absolute_percent / 100)))
            order.state = 'done'

    @api.multi
    @api.onchange('analytic_account_id')
    def onchange_analytic_account_id(self):
        """
        Trigger the change of warehouse when the analytic account is modified.
        """
        if self.analytic_account_id and self.analytic_account_id.warehouse_id:
            self.warehouse_id = self.analytic_account_id.warehouse_id
        return {}

    @api.multi
    def action_confirm(self):
        config['limit_time_real'] = None
        config['limit_time_cpu'] = None
        config['limit_time_real_cron'] = None
        for order in self:
            if order.company_id.is_manufacturer:
                _logger.error(
                    _('sale_order_gebesa inicio: %s' % order.name))
                order.validate_manufacturing()
                if not order.notify_approval:
                    raise UserError(
                        _('The following field is not invalid:\nNotify approval'))
                if not order.manufacture:
                    raise UserError(
                        _('The following field is not invalid:\nManufacture'))
                if not order.partner_shipping_id:
                    raise UserError(
                        _('The following field is not invalid:\nDelivery Address'))
                # if not order.executive:
                #     raise UserError(
                #         _('The following field is not invalid:\nExecutive'))
                if not order.priority:
                    raise UserError(
                        _('The following field is not invalid:\nManufacturing \
                          priority'))
                if not order.analytic_account_id:
                    raise UserError(
                        _('The following field is not invalid:\nAnalytic Account'))
                if not order.client_order_ref:
                    raise UserError(_('This Sales Order does not have the reference of the customer captured'))
                if not order.date_reception:
                    raise UserError(_('This Sale Order not has Date Reception'))
                for line in order.order_line:
                    if not line.route_id:
                        raise UserError(
                            _('Product line %s does not have a route assigned'
                              % (line.product_id.default_code)))
                    if line.standard_cost == 0.00:
                        raise UserError(
                            "No se puede validar un producto con costo 0 (%s)"
                            % (line.product_id.default_code))
                # Comented toda vez que ya hay un modulo de
                # PLM que considera productos cotizacion:
                # for line in order.order_line:
                #     if line.product_id.quotation_product:
                #         raise UserError(_('The Product contains Quotation'))
            else:
                order.create_product_supplierinfo()
            if order.warehouse_id != order.analytic_account_id.warehouse_id:
                raise UserError(
                    ('No coincide la Analítica con el almacen seleccionado'))
            # Validación Comentada temporalmente CEBB 12/11/2023 9.22 PM
            # for line in order.order_line:
            #     if line.low_mu and not line.margin_justification:
            #         raise UserError(
            #             'La linea del producto %s tiene un margen bajo, favor de especificar el motivo de este' % (
            #                 line.product_id.default_code))
            order.calculate_profit_margin()
            _logger.error(
                _('sale_order_gebesa fin: %s' % order.name))
        return super().action_confirm()

    @api.multi
    def validate_manufacturing(self):
        for order in self:

            # pending = self.env['sale.order'].search(
            # [('state', '=', 'draft')])
            # dife = 0.0
            # dife = order.amount_total - order.total_nste
            # if order.total_nste > 0.0000000:
            #     if abs(dife) > 0.6000:
            #         raise UserError(
            #             _('The amount are differents:\nAnalytic Account'))

            for line in order.order_line:
                if line.product_id:
                    routes = line.product_id.route_ids + \
                        line.product_id.categ_id.total_route_ids
                    if line.product_id.type == 'service':
                        continue
                    if len(routes) < 2:
                        raise UserError(
                            _('%s %s %s' % (
                                _("The next product has no a valid Route"),
                                line.product_id.default_code,
                                line.product_id.name)))
                    product_bom = False
                    for bom in line.product_id.product_tmpl_id.bom_ids:
                        if bom.product_id.id == line.product_id.id:
                            product_bom = bom or False
                    if not product_bom:
                        raise UserError(
                            _('%s %s %s' % (
                                _("The next product has no a Bill of Materials"),
                                line.product_id.default_code, line.product_id.name)))

                    # if not line.product_id.product_service_id:
                    #     raise UserError(
                    #         _('%s %s %s' % (
                    #             _("The next product has not a SAT Code: "),
                    #             line.product_id.default_code, line.product_id.name)))

    @api.multi
    def approve_action(self):
        for order in self:
            if order.approve == 'approved':
                raise UserError(_('This Sale Order is already approved'))
            if order.create_uid.id == self.env.uid:
                if order.manufacture != 'replenishment' or \
                   order.priority != 'replenishment':
                    raise UserError(_('Este no es un Pedido de Reposición solicita \
                    la aprobación de Credito y Cobranza.'))
                order.write({'approve': 'approved'})
                order.date_approved = fields.Datetime.now()
                return
            if not self.env.user.has_group('account.group_account_manager'):
                raise ValidationError(_('Este no es un Pedido de Reposición solicita \
                    la aprobación de Credito y Cobranza.'))

            if order.partner_id.over_credit and not order.partner_id.ignore_overcredit:
                raise ValidationError(_('This customer has or will have soon an over credit \
                    please review the partner terms.'))
            order.write({'approve': 'approved'})
            order.date_approved = fields.Datetime.now()

        # resws = super(SaleOrder, self)._product_data_validation()
        return

    @api.multi
    def suggested_action(self):
        for order in self:
            if order.approve == 'suggested':
                raise UserError(_('This Sale Order is already Suggested for Approval'))
            if not order.order_line:
                raise UserError(_('This Sale Order not has Products Captured'))
            if not order.client_order_ref:
                raise UserError(_('This Sales Order does not have the reference of the customer captured'))

            if order.company_id.is_manufacturer:
                # resws = order._product_data_validation()
                order.product_data_validation2()

            if order.partner_id.parent_id:
                order.partner_id = order.partner_id.parent_id
            order.write({'approve': 'suggested'})
            order.date_suggested = fields.Datetime.now()

        # if resws[0] != 'OK':
        #     raise ValidationError('Este pedido no podra ser aprobado  \
        #         debido a errores de configuracion \
        #         en los productos que ocasionarian \
        #         excepciones, se ha enviado un correo detallado a los \
        #         interesados.')

        return True

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals['perc_freight'] = self.perc_freight
        invoice_vals['perc_installation'] = self.perc_installation
        # invoice_vals['executive'] = self.executive
        invoice_vals['journal_id'] = self.analytic_account_id.journal_sale_id.id
        invoice_vals['manufacture'] = self.manufacture
        del invoice_vals['user_id']
        return invoice_vals

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        res = super().action_invoice_create(
            grouped, final)
        invoice = self.env['account.invoice'].browse(res)
        for inv in invoice:
            inv.sudo().write({
                'user_id': self.user_id and self.user_id.id})
        return res

    @api.multi
    def action_done(self):
        super().action_done()

        # commented temporary til implementatio of CRM
        self.force_quotation_send()

    @api.multi
    def force_quotation_send(self):
        for order in self:
            email_act = order.action_quotation_send()
            if email_act and email_act.get('context'):
                email_ctx = email_act['context']
                notify = order.notify_approval
                email_ctx.update(default_email_to=notify)
                email_ctx.update(default_email_from=order.company_id.email)
                order.with_context(email_ctx).message_post_with_template(email_ctx.get('default_template_id'))
        return True

    @api.multi
    def write(self, vals):
        for sale in self:
            if sale.state != 'draft':
                if sale.env.user.id == sale.env.ref('base.user_root').id:
                    if 'partner_id' in vals:
                        del vals['partner_id']
                    if 'partner_invoice_id' in vals:
                        del vals['partner_invoice_id']
                    if 'partner_shipping_id' in vals:
                        del vals['partner_shipping_id']
                    if 'user_id' in vals:
                        del vals['user_id']
        return super().write(vals)
