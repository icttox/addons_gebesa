# -*- coding: utf-8 -*-
# © 2020 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import shutil
import json
import base64
import os
import logging
from codecs import BOM_UTF8
from odoo import _, fields, api, models
from odoo.exceptions import ValidationError
import xlwt
import dropbox


BOM_UTF8U = BOM_UTF8.decode('UTF-8')
_logger = logging.getLogger(__name__)


class L10nMxSupplierTaxesStatement(models.TransientModel):
    _name = 'l10n.mx.supplier.taxes.statement'
    _description = 'descripcion pendiente'

    date_from = fields.Date(
        string='Date from',
        help='Initial date',
        required=True,
    )

    date_to = fields.Date(
        string='Date to',
        help='Final date',
        required=True,
    )

    tax_id = fields.Many2one(
        'account.tax',
        string='Tax',
        required=True,
    )

    company_id = fields.Many2one(
        'res.company',
        string='company',
        default=lambda self: self.env.user.company_id,
        required=True,
    )

    final_attach = fields.Binary(
        attachment=True,
        string="File zip")

    def fields_columns(self):
        fields_column = {
            'POLIZA_NAME': 0,
            'POLIZA_DATE': 1,
            'PARTNER_NAME': 2,
            'PARTNER_RFC': 3,
            'POLIZAPAG_NAME': 4,
            'PAGO_NAME': 5,
            'FACTURA_NAME': 6,
            'UUID': 7,
            'FACTURA_REFERENCE': 8,
            'VOUCHER_NAME': 9,
            'DESCRIPCION': 10,
            'DEBE': 11,
            'HABER': 12,
            'LOCATION': 13,
        }
        return fields_column

    def write_columns_xls(self, row_sheet, fmt, col1):
        row_sheet.write(0, col1, fmt)

    def update_to_dropbox(self, path, composename):
        key_dropbox = self.env['ir.config_parameter'].sudo().get_param(
            'l10n_mx_supplier_iva_dropbox_key', '')
        try:
            dbx = dropbox.Dropbox(key_dropbox)
            dbx.users_get_current_account()
        except dropbox.exceptions.AuthError as err:
            raise ValidationError("Dropbox log error: %s" % err)

        chunk_size = 100 * 1024 * 1024
        file_size = os.path.getsize(path)

        with open(path, 'rb') as data:
            if file_size <= chunk_size:
                dbx.files_upload(data.read(), '/' + composename + '.zip')
            else:
                upload_session_start_result = dbx.files_upload_session_start(
                    data.read(chunk_size))
                cursor = dropbox.files.UploadSessionCursor(
                    session_id=upload_session_start_result.session_id,
                    offset=data.tell())
                commit = dropbox.files.CommitInfo(path='/' + composename + '.zip')

                while data.tell() < file_size:
                    if ((file_size - data.tell()) <= chunk_size):
                        dbx.files_upload_session_finish(data.read(chunk_size),
                                                        cursor,
                                                        commit)
                    else:
                        dbx.files_upload_session_append(data.read(chunk_size),
                                                        cursor.session_id,
                                                        cursor.offset)
                        cursor.offset = data.tell()

        shared_link = dbx.sharing_create_shared_link_with_settings(
            '/' + composename + '.zip')

        return shared_link.url

    @api.multi
    def do_the_job(self):
        qselect = """SELECT
                    am.name AS poliza_name,
                    am.date AS poliza_date,
                    COALESCE(UPPER(rp.name),
                        'INTERNA') AS partner_name,
                    COALESCE(UPPER(rp.vat),
                        'NA') AS partner_rfc,
                    ampag.name AS polizapag_name,
                    ap.name AS pago_name,
                    ai.number AS factura_name,
                    ai.cfdi_uuid AS uuid,
                    ai.reference AS factura_reference,
                    av.number AS voucher_name,
                    aml.name AS descripcion,
                    aml.debit AS debe,
                    aml.credit AS haber,
                    am.id AS poliza_iva,
                    ampag.id AS poliza_pago,
                    ap.id AS pago,
                    aminv.id AS poliza_factura,
                    aminv.name AS polizafac_name,
                    ai.id AS factura,
                    av.id AS voucher
                """
        qfpurchase = """ FROM account_move_line aml
                    JOIN account_move am ON am.id = aml.move_id
                    LEFT JOIN res_partner rp ON rp.id = am.partner_id
                    LEFT JOIN account_partial_reconcile apr ON apr.id = am.tax_cash_basis_rec_id
                    LEFT JOIN account_move_line amlpag ON amlpag.id = apr.debit_move_id
                    LEFT JOIN account_account aapag ON aapag.id = amlpag.account_id
                    LEFT JOIN account_move ampag ON ampag.id = amlpag.move_id
                    LEFT JOIN account_payment ap ON ap.id = amlpag.payment_id
                    LEFT join account_partial_reconcile aprinv ON aprinv.debit_move_id = amlpag.id
                    LEFT JOIN account_move_line amlinv ON amlinv.id = aprinv.credit_move_id
                    LEFT JOIN account_move aminv ON aminv.id = amlinv.move_id
                    LEFT JOIN account_invoice ai ON ai.id = amlinv.invoice_id
                    LEFT JOIN account_payment_account_voucher_rel apav ON apav.account_payment_id = ap.id
                    LEFT JOIN account_voucher av ON av.id = apav.account_voucher_id
                """
        qfsale = """ FROM account_move_line aml
                    JOIN account_move am ON am.id = aml.move_id
                    LEFT JOIN res_partner rp ON rp.id = am.partner_id
                    LEFT JOIN account_partial_reconcile apr ON apr.id = am.tax_cash_basis_rec_id
                    LEFT JOIN account_move_line amlpag ON amlpag.id = apr.credit_move_id
                    LEFT JOIN account_account aapag ON aapag.id = amlpag.account_id
                    LEFT JOIN account_move ampag ON ampag.id = amlpag.move_id
                    LEFT JOIN account_payment ap ON ap.id = amlpag.payment_id
                    LEFT join account_partial_reconcile aprinv ON aprinv.credit_move_id = amlpag.id
                    LEFT JOIN account_move_line amlinv ON amlinv.id = aprinv.debit_move_id
                    LEFT JOIN account_move aminv ON aminv.id = amlinv.move_id
                    LEFT JOIN account_invoice ai ON ai.id = amlinv.invoice_id
                    LEFT JOIN account_payment_account_voucher_rel apav ON apav.account_payment_id = ap.id
                    LEFT JOIN account_voucher av ON av.id = apav.account_voucher_id
                """

        qwhere = """ WHERE aml.account_id = %s
                    AND aml.date >= %s
                    AND aml.date <= %s
                    AND am.company_id = %s
                """
        params = [self.tax_id.account_id.id, str(self.date_from), str(self.date_to), self.company_id.id]

        composename = str(self.id) + "_" + self.tax_id.account_id.code.replace(
            '.', '-') + "_" + str(self.date_from) + "_" + str(self.date_to)

        query = ""
        if self.tax_id.type_tax_use == 'purchase':
            query = qselect + qfpurchase + qwhere
        elif self.tax_id.type_tax_use == 'sale':
            query = qselect + qfsale + qwhere
        else:
            raise ValidationError(_(
                'Incorrect Tax type'))

        self.env.cr.execute(query, tuple(params))

        resdic = self.env.cr.dictfetchall()

        if resdic:
            path = os.path.realpath(
                os.path.join(os.path.dirname(
                    __file__), '..', 'bin', composename))
            # create directory and remove its content
            if not os.path.exists(path):
                os.makedirs(path)
            else:
                # os.chmod(attachment_dir, stat.S_IWUSR)
                shutil.rmtree(path)
                os.makedirs(path)
        else:
            raise ValidationError(_(
                'No records found for account %s:%s between dates %s -%s') % (
                self.tax_id.account_id.code, self.tax_id.account_id.name,
                str(self.date_from), str(self.date_to)))

        nwdict = []
        for rec in resdic:
            nwrec = rec
            if rec['poliza_iva']:
                path = os.path.realpath(
                    os.path.join(
                        os.path.dirname(__file__),
                        '..',
                        'bin',
                        composename,
                        rec['partner_name'].lstrip(BOM_UTF8U).replace('.', '_').replace(',', '_').replace(' ', '_') +
                        '_' +
                        rec['partner_rfc'].lstrip(BOM_UTF8U).replace(' ', '').replace('MX', '') +
                        '_' +
                        str(rec['poliza_name']).replace('/', '-')
                    ))

                # create directory and remove its content
                if not os.path.exists(path):
                    os.makedirs(path)
                else:
                    # os.chmod(attachment_dir, stat.S_IWUSR)
                    shutil.rmtree(path)
                    os.makedirs(path)

                nwrec['location'] = path
                try:
                    result = self.env.ref(
                        'l10n_mx_supplier_iva_statement.account_move_report').sudo(
                    ).render_qweb_pdf([rec['poliza_iva']])[0]
                except ValueError:
                    raise ValidationError(_(
                        'An error has occurred while accessing poliza iva report template'))

                poliza = self.env['account.move'].browse(rec['poliza_iva'])
                fname = poliza.name.replace('/', '-')

                fpath = os.path.join(path, "poliza_de_iva_" + fname + ".pdf")
                arch = open(fpath, "wb")
                arch.write(result)
                arch.close()

                # attachments account_move
                amattach = self.env['ir.attachment'].sudo().search([
                    ('res_model', '=', 'account.move'),
                    ('res_id', '=', poliza.id)])
                count = 1
                for att in amattach:
                    filenam = att.datas_fname.replace('/', '-')
                    filecont = base64.b64decode(att.datas)
                    apath = os.path.join(path, "adjunto_" + str(count) + "_" + filenam)
                    attfile = open(apath, "wb")
                    attfile.write(filecont)
                    attfile.close()
                    count += 1

                # attachments del account_move_line
                for line in poliza.line_ids:
                    amlattach = self.env['ir.attachment'].sudo().search([
                        ('res_model', '=', 'account.move.line'),
                        ('res_id', '=', line.id)])
                    count = 1
                    for att in amlattach:
                        filenam = att.datas_fname
                        filecont = base64.b64decode(att.datas)
                        apath = os.path.join(path, "adjunto_" + str(count) + "_" + filenam)
                        attfile = open(apath, "wb")
                        attfile.write(filecont)
                        attfile.close()
                        count += 1

            if rec['poliza_pago']:
                try:
                    result = self.env.ref(
                        'l10n_mx_supplier_iva_statement.account_move_report').sudo(
                    ).render_qweb_pdf([rec['poliza_pago']])[0]
                except ValueError:
                    raise ValidationError(_(
                        'An error has occurred while accessing poliza pago report template'))

                poliza = self.env['account.move'].browse(rec['poliza_pago'])
                fname = poliza.name.replace('/', '-')

                fpath = os.path.join(path, "poliza_del_pago_" + fname + ".pdf")
                arch = open(fpath, "wb")
                arch.write(result)
                arch.close()

            if rec['pago']:
                path = os.path.realpath(
                    os.path.join(
                        os.path.dirname(__file__),
                        '..',
                        'bin',
                        composename,
                        rec['partner_name'].lstrip(BOM_UTF8U).replace('.', '_').replace(',', '_').replace(' ', '_') +
                        '_' +
                        rec['partner_rfc'].lstrip(BOM_UTF8U).replace(' ', '').replace('MX', '') +
                        '_' +
                        str(rec['poliza_name']).replace('/', '-'),
                        "Pago_" + str(rec['pago_name']).replace('/', '-').replace('.', '-')))

                # create directory and remove its content
                if not os.path.exists(path):
                    os.makedirs(path)
                else:
                    # os.chmod(attachment_dir, stat.S_IWUSR)
                    shutil.rmtree(path)
                    os.makedirs(path)

                try:
                    result = self.env.ref(
                        'account_payment_report.account_payment_report').sudo(
                    ).render_qweb_pdf([rec['pago']])[0]
                except ValueError:
                    raise ValidationError(_(
                        'An error has occurred while accessing pago report template'))

                pago = self.env['account.payment'].browse(rec['pago'])
                fname = pago.name.replace('/', '-').replace('.', '-')

                fpath = os.path.join(path, "registro_de_pago_" + fname + ".pdf")
                arch = open(fpath, "wb")
                arch.write(result)
                arch.close()

                # attachments account_payment
                apattach = self.env['ir.attachment'].sudo().search([
                    ('res_model', '=', 'account.payment'),
                    ('res_id', '=', pago.id)])
                count = 1
                for att in apattach:
                    filenam = att.datas_fname.replace('/', '-')
                    filecont = base64.b64decode(att.datas)
                    apath = os.path.join(path, "adjunto_" + str(count) + "_" + filenam)
                    attfile = open(apath, "wb")
                    attfile.write(filecont)
                    attfile.close()
                    count += 1

            if rec['factura']:
                path = os.path.realpath(
                    os.path.join(
                        os.path.dirname(__file__),
                        '..',
                        'bin',
                        composename,
                        rec['partner_name'].lstrip(BOM_UTF8U).replace('.', '_').replace(',', '_').replace(' ', '_') +
                        '_' +
                        rec['partner_rfc'].lstrip(BOM_UTF8U).replace(' ', '').replace('MX', '') +
                        '_' +
                        str(rec['poliza_name']).replace('/', '-'),
                        "factura_" + str(rec['factura_name']).replace(
                            '/', '-').replace('.', '-') + '_UUID_' + str(rec['uuid'])))

                # create directory and remove its content
                if not os.path.exists(path):
                    os.makedirs(path)
                else:
                    # os.chmod(attachment_dir, stat.S_IWUSR)
                    shutil.rmtree(path)
                    os.makedirs(path)

                try:
                    result = self.env.ref(
                        'account.account_invoices').sudo(
                    ).render_qweb_pdf([rec['factura']])[0]
                except ValueError:
                    raise ValidationError(_(
                        'An error has occurred while accessing factura report template'))

                factura = self.env['account.invoice'].browse(rec['factura'])
                fnumber = factura.number or 'no_invoice'
                fuuid = factura.cfdi_uuid or 'no_uuid'
                fname = fnumber.replace('/', '-') + "_uuid_" + fuuid

                fpath = os.path.join(path, "registro_de_factura_" + fname + ".pdf")
                arch = open(fpath, "wb")
                arch.write(result)
                arch.close()

                # attachments account_invoice
                aiattach = self.env['ir.attachment'].sudo().search([
                    ('res_model', '=', 'account.invoice'),
                    ('res_id', '=', factura.id)])
                count = 1
                for att in aiattach:
                    filenam = att.datas_fname.replace('/', '-')
                    if not att.datas:
                        continue
                    filecont = base64.b64decode(att.datas)
                    if filenam.split('.')[0] != 'False':
                        apath = os.path.join(path, "adjunto_" + str(count) + "_" + filenam)
                        attfile = open(apath, "wb")
                        attfile.write(filecont)
                        attfile.close()
                        count += 1

            if rec['voucher']:
                path = os.path.realpath(
                    os.path.join(
                        os.path.dirname(__file__),
                        '..',
                        'bin',
                        composename,
                        rec['partner_name'].lstrip(BOM_UTF8U).replace('.', '_').replace(',', '_').replace(' ', '_') +
                        '_' +
                        rec['partner_rfc'].lstrip(BOM_UTF8U).replace(' ', '').replace('MX', '') +
                        '_' +
                        str(rec['poliza_name']).replace('/', '-'),
                        "voucher_" + str(rec['voucher_name']).replace(
                            '/', '-').replace('.', '-')))

                # create directory and remove its content
                if not os.path.exists(path):
                    os.makedirs(path)
                else:
                    # os.chmod(attachment_dir, stat.S_IWUSR)
                    shutil.rmtree(path)
                    os.makedirs(path)

                try:
                    result = self.env.ref(
                        'l10n_mx_supplier_iva_statement.account_voucher_report').sudo(
                    ).render_qweb_pdf([rec['voucher']])[0]
                except ValueError:
                    raise ValidationError(_(
                        'An error has occurred while accessing voucher report template'))

                voucher = self.env['account.voucher'].browse(rec['voucher'])
                fname = voucher.number.replace('/', '-')

                fpath = os.path.join(path, "registro_del_voucher_" + fname + ".pdf")
                arch = open(fpath, "wb")
                arch.write(result)
                arch.close()

                # attachments account_voucher
                aiattach = self.env['ir.attachment'].sudo().search([
                    ('res_model', '=', 'account.voucher'),
                    ('res_id', '=', voucher.id)])
                count = 1
                for att in aiattach:
                    filenam = att.datas_fname.replace('/', '-')
                    filecont = base64.b64decode(att.datas)
                    apath = os.path.join(path, "adjunto_" + str(count) + "_" + filenam)
                    attfile = open(apath, "wb")
                    attfile.write(filecont)
                    attfile.close()
                    count += 1

            nwdict.append(nwrec)

        # Reporte
        rootpath = os.path.realpath(
            os.path.join(os.path.dirname(
                __file__), '..', 'bin', composename))
        xlspath = rootpath + '/' + composename + 'resumen.xls'
        fields_columns = self.fields_columns()

        book = xlwt.Workbook()
        sheet = book.add_sheet("sheet")
        row = 0
        header_fields = list(fields_columns.keys())
        for key in header_fields:
            col = fields_columns.get(key) or 0
            head_name = key
            sheet.write(0, col, head_name)
        # import ipdb; ipdb.set_trace()
        for nwrow in nwdict:
            row += 1
            row_sheet = sheet.row(row)
            for column, pos in fields_columns.items():
                # for pylint
                # column = column
                row_sheet.write(pos, nwrow[column.lower()])
        book.save(xlspath)

        pathzipf = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'bin', composename))
        res = shutil.make_archive(pathzipf, 'zip', pathzipf)
        data = open(res, "rb").read()
        self.final_attach = base64.b64encode(data)
        # pylint: disable=W1505

        # shared_link = self.update_to_dropbox(res, composename)

        path = os.path.realpath(
            os.path.join(os.path.dirname(
                __file__), '..', 'bin', composename))

        # delete the directory and its content
        if os.path.exists(path):
            shutil.rmtree(path)
        try:
            attachment = {
                'name': composename + '.zip',
                'datas': self.final_attach,
                'datas_fname': composename + '.zip',
                'res_model': 'res.partner',
                'res_id': self.env.user.partner_id.id,
                'type': 'binary',
            }
            att = self.env['ir.attachment'].create(attachment)
            mail = self.env['mail.mail'].create({
                'subject': 'Documentos para integracion de IVA',
                'email_to': self.env.user.partner_id.email,
                'headers': "{'Return-Path': u'odoo@gebesa.com'}",
                # 'body_html': "Solicitud de documentos para integracion de IVA.<br/><a href='%s'>Descargar</a>" % shared_link,
                'body_html': "Solicitud de documentos para integracion de IVA.",
                'auto_delete': False,
                # 'attachment_ids': [(4, att.id)],
                'message_type': 'comment',
            })
            mail.send()
        except Exception as exc:
            _logger.error(
                _('L10nMxSupplierTaxesStatement ERROR: %s' % str(exc)))
        finally:
            return {
                'type': 'ir.actions.act_url',
                'url': self.get_compose_download_url(
                    _(composename) + '.zip'),
                'target': 'new',
            }

    def get_compose_download_url(self, filename, download=True):
        base_url = ("/web/content/{model}/{res_id}/final_attach/{filename}"
                    "?download={download}")
        return base_url.format(
            model=self._name, res_id=self.id, filename=filename,
            download=json.dumps(download))
