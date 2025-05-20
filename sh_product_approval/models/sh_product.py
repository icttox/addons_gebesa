# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import _, models, fields, api
from odoo.exceptions import UserError

class ShProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        res = super(ShProductTemplate, self).create(vals)
        company_id = self.env.user.company_id
        if res.type != 'product' or not company_id.is_manufacturer or res.reference_mask:
            return res
        external_ids = ["mpflrt.metal", "mpflrt.madera", "mpflrt.cajas", "mpflrt.silleria"]
        product_routes = res.route_ids.ids
        manroutes = [x.id for x in map(lambda exid: self.env.ref(exid), external_ids)]
        if bool(set(product_routes) & set(manroutes)):
            return res
        for product in res.product_variant_ids:
            self.env.cr.execute("""UPDATE product_product SET active = False, state = 'under_approval'
                WHERE id = %s""", [product.id])
        res.active = False
        return res

    # @api.multi
    # def write(self, vals):
    #     if self:
    #         # Validacion a prueba
    #         if vals.get('route_ids', False):
    #             external_ids = ["mpflrt.metal", "mpflrt.madera", "mpflrt.cajas", "mpflrt.silleria"]
    #             product_routes = self.route_ids.ids
    #             new_routes = vals.get('route_ids')[0][2]
    #             manroutes = [x.id for x in map(lambda exid: self.env.ref(exid), external_ids)]
    #             had_manuf = bool(set(product_routes) & set(manroutes))
    #             havent_manuf = not bool(set(new_routes) & set(manroutes))
    #             for product in self.with_context(active_test=False).product_variant_ids:
    #                 if had_manuf and havent_manuf and product.state == 'approved':
    #                     self.env.cr.execute("""UPDATE product_product SET active = False, state = 'under_approval'
    #                         WHERE id = %s""", [product.id])
    #                     continue

    #                 if not had_manuf and not havent_manuf and product.state != 'approved':
    #                     self.env.cr.execute("""UPDATE product_product SET active = True, state = 'approved'
    #                         WHERE id = %s""", [product.id])
    #                     continue
    #     return super(ShProductTemplate, self).write(vals)

class ShProduct(models.Model):
    _inherit = 'product.product'

    state = fields.Selection([
        ('under_approval', 'Under Approval'),
        ('approved', 'Approved'),
        ('not_approved', 'Not Approved')],
        default='approved', string="State", required=True)

    @api.multi
    def approve_product(self):
        user_id = self.env['res.users'].sudo().search([
            ('id', '=', self.env.user.id)
        ], limit=1)
        if user_id.has_group('sh_product_approval.sh_product_approve_manager'):
            for rec in self:
                if rec.state in ['not_approved', 'under_approval'] and rec.active==False:
                    rec.state = 'approved'
                    rec.active = True
                    rec.product_tmpl_id.active = True
        else:
            raise UserError(_("You are not Product Manager"))

    @api.multi
    def not_approve_product(self):
        user_id = self.env['res.users'].sudo().search([
            ('id', '=', self.env.user.id)
        ], limit=1)
        if user_id.has_group('sh_product_approval.sh_product_approve_manager'):
            for rec in self:
                if rec.state in ['under_approval', 'approved'] and rec.active==True:
                    rec.state = 'not_approved'
                    rec.active = False
                    rec.product_tmpl_id.active = False
        else:
            raise UserError(_("You are not Product Manager"))

    @api.multi
    def write(self, vals):
        for product in self:
            user_id = self.env['res.users'].sudo().search([
                ('id', '=', self.env.user.id)
            ], limit=1)
            if vals.get('state', False) and not user_id.has_group('sh_product_approval.sh_product_approve_manager'):
                raise UserError(_("You are not Product Manager"))
            if vals.get('active', False) and product.state in ['under_approval', 'not_approved'] :
                raise UserError(_("You cannot activate a not approved product"))
            # Validacion a prueba
            # if vals.get('route_ids', False):
            #     external_ids = ["mpflrt.metal", "mpflrt.madera", "mpflrt.cajas", "mpflrt.silleria"]
            #     product_routes = self.route_ids.ids
            #     new_routes = vals.get('route_ids')[0][2]
            #     manroutes = [x.id for x in map(lambda exid: self.env.ref(exid), external_ids)]
            #     had_manuf = bool(set(product_routes) & set(manroutes))
            #     havent_manuf = not bool(set(new_routes) & set(manroutes))
            #     if had_manuf and havent_manuf and self.state == 'approved':
            #         self.env.cr.execute("""UPDATE product_product SET active = False, state = 'under_approval'
            #             WHERE id = %s""", [self.id])

            #     if not had_manuf and not havent_manuf and self.state != 'approved':
            #         self.env.cr.execute("""UPDATE product_product SET active = True, state = 'approved'
            #             WHERE id = %s""", [self.id])
            if vals.get('state') in ['under_approval', 'not_approved'] and self.state in ['approved'] and self.active==True:
                vals.update({
                    'active': False
                })
                self.env.cr.execute("""UPDATE product_template SET active = False
                    WHERE id = %s""", [product.product_tmpl_id.id])
                # self.product_tmpl_id.active = False
            elif vals.get('state') in ['approved'] and product.state in ['under_approval','not_approved'] and self.active==False:
                vals.update({
                    'active': True
                })
                self.env.cr.execute("""UPDATE product_template SET active = True
                    WHERE id = %s""", [product.product_tmpl_id.id])
                # self.product_tmpl_id.active = True
        return super(ShProduct, self).write(vals)
