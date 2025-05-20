# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, exceptions, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def generate_pdf(self):
        """ Sign the xml file
        """
        attachment_obj = self.env['ir.attachment']

        # temp_report_id = self.env['ir.values'].get_default(
        #    'cfdi.config.settings', 'temp_report_id')

        # if not temp_report_id:
        report = self.env.ref(
            'report_invoice_cfdi32.account_invoices', False)
        temp_report_id = report.id

        report_obj = self.env['ir.actions.report.xml'].browse(temp_report_id)
        try:
            result = self.pool[
                'report'].get_pdf(self._cr,
                                  self._uid,
                                  [self.id],
                                  report_obj.report_name,
                                  context=self._context)
        except ValueError:
            raise exceptions.ValidationError(_(
                'An error has occurred while accessing report template'))
        att_id = attachment_obj.search([
            ('res_model', '=', str(self._model)),
            ('res_id', '=', self.id),
            ('name', '=', self.company_id.vat +
             '_' + self.number + '.pdf')], limit=1)
        return result, att_id[0].id
