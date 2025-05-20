# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from lxml import objectify
from odoo.exceptions import UserError
import base64


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    total_net_sale = fields.Float(
        string='Total Net Sale',
        digits=dp.get_precision('Account'),
    )

    perc_freight = fields.Float(
        string='Freight Percentage',
        digits=dp.get_precision('Account'),
    )

    total_freight = fields.Float(
        string='Total Freight',
        digits=dp.get_precision('Account'),
    )

    perc_installation = fields.Float(
        string='Installation Percentage',
        digits=dp.get_precision('Account'),
    )

    total_installation = fields.Float(
        string='Total Installation',
        digits=dp.get_precision('Account'),
    )

    profit_margin = fields.Float(
        string='Profit Margin',
        digits=dp.get_precision('Account'),
    )

    not_be_billed = fields.Boolean(
        string='Not be Billed',
    )

    manufacture = fields.Selection(
        [('special', 'Special'),
            ('line', 'Line'),
            ('replenishment', 'Replenishment'),
            ('semi_special', 'Semi special')],
        string="Manufacture",

    )

    total_cost = fields.Float(
        string='Total Cost',
        digits=dp.get_precision('Account'),
    )

    executive = fields.Char(
        string='Executive',
        size=100,
    )

    portfolio_type = fields.Selection(
        [('attested_copy', 'Attested copy'),
         ('national', 'National'),
         ('foreign', 'Foreign'),
         ('street_market', 'Street market'),
         ('replacement', 'Replacement'),
         ('bad_debt', 'Bad debt'),
         ('sample', 'Sample'),
         ('agreement', 'Agreement'),
         ('legal', 'Legal')],
        string="Portfolio type",
        states={'cancel': [('readonly', True)]},
        store=True,
        index=True,
        default='national',
    )

    itinerary = fields.Integer(
        'Itinerary',
        help='Itinerary number')

    @api.onchange('account_analytic_id', 'company_id')
    def _onchange_account_analytic_id(self):
        """Inherit to set account_journal assigned in the
        analytic."""
        res = ""
        # res = super(AccountInvoice, self)._onchange_account_analytic_id()
        if self.type in ('out_invoice'):
            self.journal_id = self.account_analytic_id.journal_sale_id
        return res

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.partner_id:
            self.currency_id = self.partner_id.property_product_pricelist.currency_id.id
        else:
            super()._onchange_journal_id()

    @api.multi
    def set_quantities_from_xml(self):
        for rec in self:
            xml_attachment = self.env['ir.attachment'].search(
                [('res_model', '=', 'account.invoice'),
                 ('res_id', '=', rec.id)]).filtered(
                lambda att: att.name[-4:].upper() == '.XML')

            if not xml_attachment:
                raise UserError(("No XML file found"))

            if len(xml_attachment) > 1:
                raise UserError(("More than 1 XML found"))

            xml_cfdi = objectify.fromstring(base64.decodestring(xml_attachment.datas))

            ns_map = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}

            conceptos = xml_cfdi.find('cfdi:Conceptos', namespaces=ns_map)

            # Apply the same logic to the above example data
            aggregate_concepts = {}
            for concepto in conceptos.iterchildren():
                no_identificacion = concepto.get('NoIdentificacion')
                cantidad = float(concepto.get('Cantidad'))

                if no_identificacion not in aggregate_concepts:
                    aggregate_concepts[no_identificacion] = 0
                aggregate_concepts[no_identificacion] += cantidad

            consolidado = tuple(
                {'NoIdentificacion': key, 'Cantidad': value} for key, value in aggregate_concepts.items()
            )
            product_ids = []

            for elemento in consolidado:
                product = self.env['product.product'].search([
                    ('default_code', '=', elemento['NoIdentificacion'])
                ])
                if not product:
                    product = self.env['product.product'].with_context(
                        active_test=False).search([
                            ('default_code', '=', elemento['NoIdentificacion'])
                        ])

                product_ids.append(product.id)
                inv_lines = self.env['account.invoice.line'].search([
                    ('invoice_id', '=', rec.id),
                    ('product_id', '=', product.id),
                    ('quantity', '>', 0),
                    # ('state', 'not in', ('cancel', 'done'))
                ])

                remaining = float(elemento['Cantidad'])

                for line in inv_lines:
                    if line.quantity < remaining:
                        # line.write({'quantity': line.quantity})
                        remaining = remaining - line.quantity
                    else:
                        line.write({'quantity': remaining})
                        remaining = remaining - remaining

                if remaining > 0.00:
                    raise UserError(
                        _("There is a remaining quantity %s of this product %s probably you uploaded a wrong XML file") % (remaining, product.default_code + ' - ' + product.product_tmpl_id.name))

            inv_lines = self.env['account.invoice.line'].search([
                ('invoice_id', '=', rec.id),
                ('quantity', '=', 0),
            ])
            inv_lines.unlink()
            inv_lines = self.env['account.invoice.line'].search([
                ('invoice_id', '=', rec.id),
                ('product_id', 'not in', product_ids),
                ('quantity', '>', 0),
            ])
            inv_lines.unlink()
