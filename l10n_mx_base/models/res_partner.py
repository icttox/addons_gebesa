# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class ResPartner(models.Model):
    """Inherited to complete the attributes required to fiscal documents.

    **Toponyms**

    Added new field in partner address to complete the Mexico
    toponyms and allow have all fields required in XML fiscal.
    Locality is added to set this value in the address.

    **Fiscal Regime**
    The fiscal regimen catalog is provided by the SAT `here <goo.gl/mwcbtx>`
    """
    _inherit = 'res.partner'

    l10n_mx_payment_method_id = fields.Many2one(
        'l10n_mx.payment.method', 'Payment Method',
        help='Define a default value to payment method on invoices created to '
        'this customer. When you create a new invoice to this customer, the '
        'default value will be the assigned here.\n'
        'The payment method in the invoice is to indicate which method is '
        'used to pay the invoice, and are provided by the SAT.',
    )

    l10n_mx_locality = fields.Char(
        'Locality', help='Optional attribute used in the XML that serves to '
        'define the city or town where the location is given')

    l10n_mx_edi_usage = fields.Selection(
        '_get_l10n_mx_edi_usages', 'Usage',
        help='Used in the XML to express the key to the use that gives the '
        'receiver to the invoices generated to this customer.')

    def _get_default_country(self):
        country = self.env.ref('base.mx').id
        if self.env.user.company_id.country_id:
            country = self.env.user.company_id.country_id.id
        return country

    country_id = fields.Many2one(default=_get_default_country)

    def _get_l10n_mx_edi_usages(self):
        return [
            ('G01', _('Acquisition of merchandise')),
            ('G02', _('Returns, discounts or bonuses')),
            ('G03', _('General expenses')),
            ('I01', _('Constructions')),
            ('I02', _('Office furniture and equipment investment')),
            ('I03', _('Transportation equipment')),
            ('I04', _('Computer equipment and accessories')),
            ('I05', _('Dices, dies, molds, matrices and tooling')),
            ('I06', _('Telephone communications')),
            ('I07', _('Satellite communications')),
            ('I08', _('Other machinery and equipment')),
            ('D01', _('Medical, dental and hospital expenses.')),
            ('D02', _('Medical expenses for disability')),
            ('D03', _('Funeral expenses')),
            ('D04', _('Donations')),
            ('D05', _(
                'Real interest effectively paid for mortgage loans '
                '(room house)')),
            ('D06', _('Voluntary contributions to SAR')),
            ('D07', _('Medical insurance premiums')),
            ('D08', _('Mandatory School Transportation Expenses')),
            ('D09', _(
                'Deposits in savings accounts, premiums based on pension '
                'plans.')),
            ('D10', _('Payments for educational services (Colegiatura)')),
            ('S01', _('No tax effects')),
            ('CP01', _('Payments')),
            ('CN01', _('Payroll')),
            ('P01', _('To define'))]
