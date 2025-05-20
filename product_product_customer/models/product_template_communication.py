# Copyright 2022, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _


class ProductTemplatePartnerCommunication(models.Model):
    _name = 'product.template.partner.communication'
    _description = 'Sometimes production needs to be informed for some customer '
    'or supplier communication, this module meant to deal eith this need'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    partner_communication = fields.Text(
        string='Partner communication',
        translate=True,
        required=True,
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Parner',
        required=True,
    )

    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Product',
        required=True,
    )

    _sql_constraints = [
        ('partner_product_unique',
         'unique(partner_id, product_tmpl_id)',
         _('A communication already exists for this customer and product.')),
    ]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_communication_ids = fields.One2many(
        'product.template.partner.communication',
        'product_tmpl_id',
        string='Partner communications',
    )

    @api.multi
    def action_view_partner_communication(self):
        action = self.env.ref(
            'product_product_customer.view_partner_product_communication_action').read()[0]
        action['domain'] = [('id', 'in', self.product_communication_ids.ids)]
        return action
