# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    factoraje_v2 = fields.Boolean(
        string='Factoraje',
        help='Se aplico factoraje',
    )
    factoraje_journal_id = fields.Many2one(
        'account.journal',
        string='Diario del factoraje',
    )

    @api.multi
    def action_factoraje(self):
        # model_obj = self.env['ir.model.data']

        for inv in self:
            if not inv.factoraje_journal_id:
                raise ValidationError(
                    _(u"El campo 'Diario del factoraje' no es valido"))

        # model, action_id = model_obj.get_object_reference(
        #    'account', 'action_account_invoice_payment')
        # action = self.pool[model].read(
        #    self._cr, self._uid, action_id, context=self._context)
        action = self.env.ref('account.action_account_invoice_payment').read()[0]
        action['context'] = {
            'default_invoice_ids': [(4, self.id, None)],
            'default_journal_id': self.factoraje_journal_id.id,
            'default_payment_date': self.date_due,
            'default_prepayment_type': 'factoraje',
            'default_account_analytic_id': self.account_analytic_id.id}
        return action
