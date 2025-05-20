
from odoo import models, fields, api


class TmsWizardRealAmount(models.TransientModel):
    _name = 'tms.wizard.real.amount'
    _description = 'descripcion pendiente'

    real_amount = fields.Boolean(
        string='Monto Real',
    )

    @api.multi
    def print_real_amount(self):
        ids = self.env.context['active_ids']
        travel = self.env['tms.travel'].search([('id', '=', ids)])
        ctx = dict(self.env.context or {},
                   active_ids=ids,
                   active_model='tms.travel',
                   real_amount=self.real_amount)
        data = {}
        data['form'] = self.read(['real_amount'])[0]

        #  return self.env['report'].get_action(travel, 'flete_gebesa.report_carta_porte_travel', data=data)
        return {'type': 'ir.actions.report',
                'report_name': 'flete_gebesa.report_carta_porte_travel',
                'report_type': 'qweb-pdf',
                'data': data,
                'context': ctx,
                }
