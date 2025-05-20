# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class AccountInvoice(models.Model):
    """The invoice has been modified to map the fields in Odoo to the legally
    required electronic format.

    Mapping fields:

    An attribute called `invoice_cfdi_v32` make a map between the names in
    field in odoo and the name in the xml (or the cfdilib) used to make the
    mapping and  create the an invoice object.

    You can see the template here: https://goo.gl/aUf0qR
    You can see the legal xsd annotated with its documentation of the elements
    here: https://goo.gl/M9a6Po
    """
    _inherit = 'account.invoice'

    # Nombre en version 11 base l10n_mx_address_issued_id
    address_issued_id = fields.Many2one(
        'res.partner', string='Address Issued',
        help='Issued address to XML generated with the invoice. This value is '
        'taken from journal or company the invoice address.')

    sello = fields.Text('Stamp', help='Digital Stamp')

    pac_id = fields.Many2one(
        related='journal_id.sequence_id.pac_id', relation='res.pac',
        help='Pac used in signed of this invoice. This value is taken from '
        'journal sequence.', string='PAC')

    validate_uuid_sat = fields.Char(
        'CFID status in the SAT System',
        help='UUID status in SAT system.')

    sequence_id = fields.Many2one(
        'ir.sequence',
        store=True,
        help='Sequence used in the invoice, necessary to compute correctly the'
        ' information of folios used by sale invoices and sale refunds'
        '(documents signed)')

    l10n_mx_payment_method_id = fields.Many2one(
        'l10n_mx.payment.method', string='Payment Method', readonly=True,
        states={'draft': [('readonly', False)]},
        help='Indicates the way it was paid or will be paid the invoice, '
        'where the options could be: Cash, Nominal Check, Credit Card, etc. '
        'If not know as will be paid the invoice, leave empty and the XML '
        'show "Unidentified".',
    )

    account_payment_id = fields.Many2one(
        'res.partner.bank', string='Account Payment', readonly=True,
        states={'draft': [('readonly', False)]},
        domain="[('partner_id', '=', partner_id)]",
        help='Is the account which the client will pay from, if not '
        'know which account will used for pay leave empty and the XML will '
        'show "Unidentified".')  # TODO - Remove field with CFDI 3.3

    # l10n_mx_payment_terms = fields.Char(
    #     related='payment_term_id.l10n_mx_payment_terms',
    #     string='Payment Terms',
    #     help='Attribute to specify the payment method that applies to this '
    #     'digital document via the Internet. It is used to express a single '
    #     'installment payment or paid number of bias against total bias, '
    #     'partiality 1 X.')

    record_size = fields.Char(
        help="for the sake of debugging this technical field will represent "
             "the size of the record it is computed on the fly then you can "
             "know in any time if the xml information is impacting the "
             "performance.")

    cfdi_cancellation_date = fields.Datetime(
        'CFDI Cancellation Date', help='If the invoice is cancel, this field '
        'saved the date when is cancel', copy=False)
    xml = fields.Text('XML', help='Raw XML before being signed.', copy=False)

    xml_signed = fields.Text('XML Signed', help='Raw XML after being signed.',
                             copy=False)

    json = fields.Text(help='Raw json before being converted to XML.',
                       copy=False)

    document_type = fields.Char(
        help='CFDI v3.3 request the field "tipoDeComprobante".\n'
        'For customer invoice is: "I".\nFor customer refund is: "E".')

    last_acc_number = fields.Char(
        'Last 4 bank account digits',
        related='account_payment_id.last_acc_number',
        help="CFDI v3.2 request the last 4 digits of a bank account number"
        " for the field 'NumCtaPago' of xml.")  # noqa TODO - Remove field with CFDI 3.3, is not required

    # Existe otro campo en 11 base con este mismo nombre que no tiene que ver con
    # CFDi
    certificate_old = fields.Char(
        help='Read the certificate file configured in the company, and return '
        'the content in string.')

    certificate_number = fields.Char(
        help='Certificate Serial Number, is obtained by the certificate '
        'configured in the company.')

    cfdi_original_string = fields.Text(
        'Original String', copy=False,
        help='Original String returned by the SAT, is used in PDF report.')

    date_stamped = fields.Datetime(
        copy=False,
        help='Date when is stamped the electronic invoice')

    #  Nombre en version 11 base l10n_mx_edi_cfdi_uuid
    cfdi_uuid = fields.Char(
        'Fiscal Folio', copy=False, index=True,
        help='Folio in electronic invoice, returned by SAT.',)

    l10n_mx_report_name = fields.Char(help="File Name for new Attachment",
                                      readonly=True)
    cert_msg = fields.Text(
        string='Message',
        help="Messages displayed when the certificate is about to expire")
