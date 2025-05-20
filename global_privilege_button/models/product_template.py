# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, _, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals_list):
        if not self.env.user.has_group(
                'global_privilege_button.group_manager_product'):
            raise UserError(_('Error!\nYou do not have privileges to Create'
                              ' Product(s).\nCheck with your'
                              ' System Administrator.'))
        if 'is_line' in vals_list.keys():
            if vals_list.get('is_line') is True and \
               not self.env.user.has_group('global_privilege_button.group_manager_is_line_product'):
                raise UserError(_('Error!\nYou do not have privileges to Create'
                                  ' Line Products.'))

        ctx = self._context.copy()
        ctx.update({'mail_create_nosubscribe': True})
        self = self.with_context(ctx)
        return super().create(vals_list)

    @api.one
    def write(self, vals):
        if not self.env.user.has_group(
                'global_privilege_button.group_manager_product'):
            raise UserError(_('Error!\nYou do not have privileges to Modify'
                              ' Product(s).\nCheck with your'
                              ' System Administrator.'))
        if 'active' in vals.keys():
            if vals.get('active') is False and self.sudo().qty_available != 0:
                raise UserError(_('Error!\nNo puede Inactivar un Producto con'
                                  ' existencia en el Sistema.'))

        # reference_mask,attribute_line_ids,name,sale_ok,purchase_ok,type,default_code,product_service_id,is_line,family_id,group_id,line_id,route_ids,categ_id,tracking,invoice_policy,description_sale,standard_price
        critical_fields = {'reference_mask', 'attribute_line_ids',
                           'name', 'sale_ok', 'purchase_ok', 'type',
                           'product_service_id', 'is_line', 'family_id',
                           'group_id', 'line_id', 'route_ids', 'categ_id',
                           'tracking', 'invoice_policy',
                           'description_sale', 'standard_price', 'default_code'}

        need_val = False
        for field in critical_fields:
            if field in vals.keys():
                need_val = True

        # if len(vals.keys()) > 0:
        if need_val:
            if 'is_line' in vals.keys() and not self.env.user.has_group(
                    'global_privilege_button.group_manager_is_line_product'):
                raise UserError(_('Error!\nYou do not have privileges \
                                to Set Line Products.'))

            if self.is_line is True and not self.env.user.has_group(
                    'global_privilege_button.group_manager_is_line_product'):
                raise UserError(_('Error!\nYou do not have privileges \
                                to Modify Line Products.\n You are \
                                modifying: %s') % (vals))

        return super().write(vals)

    @api.multi
    def unlink(self):
        if not self.env.user.has_group(
                'global_privilege_button.group_manager_product'):
            raise UserError(_('Error!\nYou do not have privileges to Delete'
                              ' Product(s).\nCheck with your'
                              ' System Administrator.'))
        return super().unlink()
