# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    general_tag_num = fields.Char(
        string='General tag number',
        help='Description number for the entire order',
    )

    contract_num = fields.Char(
        string='Contract number',
        help='Contract number',
    )

    delivery_instruction = fields.Char(
        string='Delivery Instruction',
    )

    @api.multi
    def action_quotation_send(self):

        action = super().action_quotation_send()
        #import pdb; pdb.set_trace()
        # model = 'sale'
        # template = 'email_template_edi_sale'

        # if(self.partner_id.country_id.code == 'US'):
        model = 'paperwork_usa'
        template = 'email_template_edi_usa'

        ir_model_data = self.env['ir.model.data']

        quote_template_id = self.read(['template_id'], ['template_id'])

        execute_ack = self.env.context.get('execute_acknowledgement')
        if self.company_id.country_id.code != 'MX' and not execute_ack:
            return

        if quote_template_id:
            try:
                template_id = ir_model_data.get_object_reference(
                    model, template)[1]
            except ValueError:
                pass
            else:
                action['context'].update({
                    'default_template_id': template_id,
                    'default_use_template': True
                })
        return action
