# -*- coding: utf-8 -*-

import datetime
from pytz import timezone
import requests

from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp
from odoo.addons.l10n_mx_edi.models.account_invoice import create_list_html
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    l10n_mx_edi_incoterm = fields.Selection(
        [('CIP', 'CARRIAGE AND INSURANCE PAID TO'),
         ('CPT', 'CARRIAGE PAID TO'),
         ('CFR', 'COST AND FREIGHT'),
         ('CIF', 'COST, INSURANCE AND FREIGHT'),
         ('DAF', 'DELIVERED AT FRONTIER'),
         ('DAP', 'DELIVERED AT PLACE'),
         ('DAT', 'DELIVERED AT TERMINAL'),
         ('DDP', 'DELIVERED DUTY PAID'),
         ('DDU', 'DELIVERED DUTY UNPAID'),
         ('DEQ', 'DELIVERED EX QUAY'),
         ('DES', 'DELIVERED EX SHIP'),
         ('EXW', 'EX WORKS'),
         ('FAS', 'FREE ALONGSIDE SHIP'),
         ('FCA', 'FREE CARRIER'),
         ('FOB', 'FREE ON BOARD')],
        string='Incoterm',
        default='EXW',
        help='Indicates the INCOTERM applicable to the'
        'external trade customer invoice.')
    l10n_mx_edi_cer_source = fields.Char(
        'Certificate Source',
        help='Used in CFDI like attribute derived from the exception of '
        'certificates of Origin of the Free Trade Agreements that Mexico '
        'has celebrated with several countries. If have a value, will to '
        'indicate that funge as certificate of origin and this value will be '
        'set in the CFDI nose "NumCertificadoOrigen".')
    l10n_mx_edi_external_trade = fields.Boolean(
        'Need external trade?',
        compute='_compute_need_external_trade',
        inverse='_inverse_need_external_trade', store=True,
        help='If this field is active, the CFDI that generate this invoice '
        'will to include the complement "External Trade".')

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super()._onchange_partner_id()
        if self.partner_id.l10n_mx_edi_external_trade and self.type == 'out_invoice':
            self.l10n_mx_edi_incoterm = 'EXW'
        return res

    @api.depends('partner_id')
    def _compute_need_external_trade(self):
        """Assign the "Need external trade?" value how in the partner"""
        for record in self.filtered(lambda i: i.type == 'out_invoice'):
            record.l10n_mx_edi_external_trade = record.partner_id.l10n_mx_edi_external_trade

    def _inverse_need_external_trade(self):
        return True

    @api.model
    def l10n_mx_edi_get_complement_external_trade_version(self):
        '''Returns the cfdi version to generate the CFDI.
        '''
        version = self.env['ir.config_parameter'].sudo().get_param(
            'l10n_mx_edi_cfdi_complement_external_trade_version', '2.0')
        return version

    @api.depends('l10n_mx_edi_external_trade')
    def _compute_l10n_mx_edi_export(self):
        for inv in self:
            if not inv.l10n_mx_edi_external_trade:
                inv.l10n_mx_edi_export = '01'
            else:
                inv.l10n_mx_edi_export = '02'

    @api.multi
    def action_invoice_open(self):
        for invoice in self:
            if all(line.product_id.type == 'service' for line in invoice.invoice_line_ids):
                invoice.l10n_mx_edi_external_trade = False
        return super().action_invoice_open()

    @api.multi
    def _perform_l10n_mx_validations(self):
        res = super()._perform_l10n_mx_validations()
        if not self.l10n_mx_edi_external_trade:
            return res
        bad_line = self.invoice_line_ids.filtered(
            lambda l: not l.product_id.weight or not l.product_id.l10n_mx_edi_umt_aduana_id or
            (l.product_id.l10n_mx_edi_umt_aduana_id.l10n_mx_edi_code_aduana != '99' and not l.product_id.l10n_mx_edi_tariff_fraction_id))
        if bad_line:
            line_name = bad_line.mapped('product_id.name')
            raise UserError(_(
                'Verifica por favor que Qty UMT tenga un valor en la linea, '
                'y que el producto tiene capturado un valor en fracción afancelaria '
                'unidad de medida UMT y peso.<br/><br/>En estos productos:'
            ) + create_list_html(line_name))
        return res

    def _get_currency_rate_banxico_sat(self):
        foreigns = {
            'EUR': 'SF46410',
            'CAD': 'SF60632',
            'JPY': 'SF46406',
            'GBP': 'SF46407',
            'USD': 'SF60653',
        }

        icp = self.env['ir.config_parameter'].sudo()
        token = icp.get_param('banxico_token')
        if not token:
            # https://www.banxico.org.mx/SieAPIRest/service/v1/token
            token = 'd03cdee20272f1edc5009a79375f1d942d94acac8348a33245c866831019fef4'
            icp.set_param('banxico_token', token)
        url = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/%s/datos/%s/%s?token=%s'
        if not self.date_invoice:
            date_mx = datetime.datetime.now(timezone('America/Mexico_City'))
        else:
            date_mx = self.date_invoice
        today = date_mx.strftime(DEFAULT_SERVER_DATE_FORMAT)

        try:
            res = requests.get(url % (foreigns[self.currency_id.name], today, today, token))
            res.raise_for_status()
            data = res.json()['bmx']['series'][0]
        except Exception as e:
            raise UserError('Error al conectar a banxico %s' % e)
        if 'datos' not in data:
            today = (date_mx - datetime.timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
            try:
                res = requests.get(url % (foreigns[self.currency_id.name], today, today, token))
                res.raise_for_status()
                data = res.json()['bmx']['series'][0]
            except Exception as e:
                raise UserError('Error al conectar a banxico %s' % e)
            if 'datos' not in data:
                raise UserError(
                    'No se encontro un tipo de cambio para esta factura en el portal de banxico')
        return float(data['datos'][0]['dato'])

    @api.multi
    def _l10n_mx_edi_create_cfdi(self):
        if not self.l10n_mx_edi_external_trade:
            return super()._l10n_mx_edi_create_cfdi()

        # Call the onchange to obtain the values of l10n_mx_edi_qty_umt
        # and l10n_mx_edi_price_unit_umt, this is necessary when the
        # invoice is created from the sales order or from the picking
        self.invoice_line_ids.onchange_quantity()
        self.invoice_line_ids._set_price_unit_umt()

        bad_line = self.invoice_line_ids.filtered(
            lambda l: not l.l10n_mx_edi_qty_umt or not l.l10n_mx_edi_umt_aduana_id or
            (l.l10n_mx_edi_umt_aduana_id.l10n_mx_edi_code_aduana != '99' and not l.l10n_mx_edi_tariff_fraction_id))
        if bad_line:
            line_name = bad_line.mapped('product_id.name')
            return {'error': _(
                'Please verify that Qty UMT has a value in the line, '
                'and that the product has set a value in Tariff Fraction and '
                'in UMT Aduana.<br/><br/>This for the products:'
            ) + create_list_html(line_name)}
        return super()._l10n_mx_edi_create_cfdi()

    @api.multi
    def _l10n_mx_edi_create_cfdi_values(self):
        """Create the values to fill the CFDI template with external trade.
        """
        values = super()._l10n_mx_edi_create_cfdi_values()

        if self.l10n_mx_edi_get_customer_rfc() == 'XEXX010101000':
            values.update({
                'receiver_reg_trib': values['customer'].vat,
            })
        if not self.l10n_mx_edi_external_trade:
            return values

        complement_version = self.l10n_mx_edi_get_complement_external_trade_version()
        values['complement_external_trade_version'] = complement_version

        ctx = dict(company_id=self.company_id.id, date=self.date_invoice)
        # customer = values['customer']
        values.update({
            'usd': self.env.ref('base.USD').with_context(ctx),
            'mxn': self.env.ref('base.MXN').with_context(ctx),
            'europe_group': self.env.ref('base.europe'),
            # 'receiver_reg_trib': customer.vat,
        })

        # 07 Jun 2023 Banxico's webservice is failing
        # that's why we need to create manually this parameter and set the
        # current rate
        icp = self.env['ir.config_parameter'].sudo()
        rate_sat = icp.get_param('banxico_rate_usd')
        if not rate_sat:
            rate_sat = self._get_currency_rate_banxico_sat()
        values['quantity_aduana'] = lambda p, i: sum([
            line.l10n_mx_edi_qty_umt for line in i.invoice_line_ids
            if line.product_id == p])
        values['unit_value_usd'] = lambda l, c, u: c.compute(
            l.l10n_mx_edi_price_unit_umt, u)
        values['amount_usd'] = rate_sat
        # values['total_usd'] = lambda i, u, c: sum([
        #     round(line.l10n_mx_edi_qty_umt * c._convert_mxn(
        #         line.l10n_mx_edi_price_unit_umt, u, self.company_id, self.date_invoice), 2) for line in i])
        values['amount_from_concepto'] = lambda p, i: sum([
            line.price_subtotal for line in i.invoice_line_ids
            if line.product_id == p])
        return values

    @api.model
    def l10n_mx_edi_get_et_etree(self, cfdi):
        """Get the ComercioExterior node from the cfdi.
        :param cfdi: The cfdi as etree
        :return: the ComercioExterior node
        """
        if not hasattr(cfdi, 'Complemento'):
            return None

        complement_version = self.l10n_mx_edi_get_complement_external_trade_version()
        if complement_version == '1.1':
            attribute = 'cce11:ComercioExterior[1]'
            namespace = {'cce11': 'http://www.sat.gob.mx/ComercioExterior11'}
        elif complement_version == '2.0':
            attribute = 'cce20:ComercioExterior[1]'
            namespace = {'cce20': 'http://www.sat.gob.mx/ComercioExterior20'}
        else:
            return None
        node = cfdi.Complemento.xpath(attribute, namespaces=namespace)
        return node[0] if node else None


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    l10n_mx_edi_tariff_fraction_id = fields.Many2one(
        'l10n_mx_edi.tariff.fraction', 'Tariff Fraction',
        store=True,
        related='product_id.l10n_mx_edi_tariff_fraction_id',
        readonly=True,
        compute_sudo=True,
        help='It is used to express the key of the tariff fraction '
        'corresponding to the description of the product to export. Node '
        '"FraccionArancelaria" to the concept.')
    l10n_mx_edi_umt_aduana_id = fields.Many2one(
        'uom.uom', 'UMT Aduana',
        store=True,
        related='product_id.l10n_mx_edi_umt_aduana_id',
        readonly=True,
        compute_sudo=True,
        help='Used in complement "Comercio Exterior" to indicate in the '
        'products the TIGIE Units of Measurement, this based in the SAT '
        'catalog.')
    l10n_mx_edi_qty_umt = fields.Float(
        'Qty UMT', help='Quantity expressed in the UMT from product. Is '
        'used in the attribute "CantidadAduana" in the CFDI',
        digits=dp.get_precision('Product Unit of Measure'))
    l10n_mx_edi_price_unit_umt = fields.Float(
        'Unit Value UMT', help='Unit value expressed in the UMT from product. '
        'Is used in the attribute "ValorUnitarioAduana" in the CFDI')

    @api.multi
    def _set_price_unit_umt(self):
        for res in self:
            res.l10n_mx_edi_price_unit_umt = round(
                res.quantity * res.price_unit / res.l10n_mx_edi_qty_umt
                if res.l10n_mx_edi_qty_umt else
                res.l10n_mx_edi_price_unit_umt, 2)

            if res.discount and not res.invoice_id.break_down_disc:
                res.l10n_mx_edi_price_unit_umt = round(
                    res.quantity * (res.price_unit - (
                        round(res.price_unit * (res.discount / 100), 2))) / res.l10n_mx_edi_qty_umt
                    if res.l10n_mx_edi_qty_umt else
                    res.l10n_mx_edi_price_unit_umt, 2)

            res.l10n_mx_edi_qty_umt = round(
                res.quantity * res.price_unit / res.l10n_mx_edi_price_unit_umt
                if res.l10n_mx_edi_price_unit_umt else
                res.l10n_mx_edi_qty_umt, 3)

            if res.discount and not res.invoice_id.break_down_disc:
                res.l10n_mx_edi_qty_umt = round(
                    res.quantity * (res.price_unit - (
                        round(res.price_unit * (res.discount / 100), 2))) / res.l10n_mx_edi_price_unit_umt
                    if res.l10n_mx_edi_price_unit_umt else
                    res.l10n_mx_edi_qty_umt, 3)

    @api.onchange('quantity', 'product_id', 'l10n_mx_edi_umt_aduana_id')
    @api.multi
    def onchange_quantity(self):
        """When change the quantity by line, update the QTY in the UMT"""
        for res in self.filtered(
                lambda l: l.invoice_id.l10n_mx_edi_external_trade and
                l.product_id):
            pdt_aduana = res.l10n_mx_edi_umt_aduana_id.l10n_mx_edi_code_aduana
            pdt_product = res.uom_id.l10n_mx_edi_code_aduana
            if pdt_aduana == pdt_product:
                res.l10n_mx_edi_qty_umt = res.quantity
            elif pdt_aduana and '06' == pdt_aduana and pdt_product in ('12', 'SET'):
                res.l10n_mx_edi_qty_umt = res.quantity
            elif pdt_aduana and '01' in pdt_aduana:
                res.l10n_mx_edi_qty_umt = round(
                    res.product_id.weight * res.quantity, 3)
