# -*- coding: utf-8 -*-
# © 2017 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.osv import expression


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    # @api.model
    # def _search_rule(self, product_id, values, domain):
    #     """ Este inherit es el que hace que para escoger la regla a ejecutar
    #         se tenga en cuenta la ubicacion que tiene la linea del BoM
    #     """
    #     if values.get('move_dest_ids', False):
    #         location_mbl = False
    #         bom_id = values.get(
    #             'move_dest_ids', False).raw_material_production_id.bom_id
    #         if bom_id:
    #             location_mbl = self.env['mrp.bom.line'].search(
    #                 [('bom_id', '=', bom_id.id),
    #                  ('product_id', '=', product_id.id)], limit=1).location_id
    #         else:
    #             for dom in domain:
    #                 if dom[0] == 'location_id':
    #                     location = self.env['stock.location'].browse(dom[2])
    #             bom_id = self.env['mrp.bom'].search([
    #                 ('product_id', '=', product_id.id),
    #                 ('active', '=', True)])
    #             if bom_id and bom_id.routing_id:
    #                 location_dest = bom_id.routing_id.location_id
    #                 if (location.id != location_dest.id and
    #                         location.stock_warehouse_id.id == location_dest.stock_warehouse_id.id):
    #                     location_mbl = location_dest
    #             # import ipdb; ipdb.set_trace()
    #         if location_mbl:
    #             domain = expression.AND([
    #                 [('location_src_id', '=', location_mbl.id)], domain])
    #     res = super(ProcurementGroup, self)._search_rule(
    #         product_id, values, domain)
    #     return res

    @api.model
    def run_scheduler(self, use_new_cursor=False, company_id=False):
        ctx = self._context.copy()
        ctx.update({
            'replenishment_manual': True,
            'default_approved_to_produce': True,
        })
        return super(ProcurementGroup, self.with_context(ctx)).run_scheduler(use_new_cursor, company_id)

    @api.model
    def _get_rule(self, product_id, location_id, values):
        """ Find a pull rule for the location_id, fallback on the parent
        locations if it could not be found.
        """
        location_mbl = False
        is_manufacturer = values.get('company_id').is_manufacturer or False
        if (values.get('move_dest_ids', False) and is_manufacturer) or self.env.context.get('replenishment_manual', False):
            bom_id = False
            if 'move_dest_ids' in values and not values.get('company_id').skip_supply_mo:
                bom_id = values.get(
                    'move_dest_ids', False).raw_material_production_id.bom_id
            if bom_id:
                location_mbl = self.env['mrp.bom.line'].search(
                    [('bom_id', '=', bom_id.id),
                     ('product_id', '=', product_id.id)], limit=1).location_id
            else:
                bom_id = self.env['mrp.bom'].search([
                    ('product_id', '=', product_id.id),
                    ('active', '=', True)])
                if bom_id and bom_id.routing_id:
                    location_dest = bom_id.routing_id.location_id
                    if (location_id.id != location_dest.id
                            and location_id.stock_warehouse_id.id == location_dest.stock_warehouse_id.id):
                        location_mbl = location_dest
                # import ipdb; ipdb.set_trace()

        result = False
        location = location_id
        while (not result) and location:
            domain = [
                ('location_id', '=', location.id),
                ('action', '!=', 'push')]
            if location_mbl:
                domain = expression.AND([
                    [('location_src_id', '=', location_mbl.id)], domain])
            result = self._search_rule(
                values.get('route_ids', False),
                product_id,
                values.get('warehouse_id', False),
                domain)
            location = location.location_id
        return result


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(
            self, product_id, product_qty, product_uom, location_id, name,
            origin, values, bom):
        email_to = 'sistemas@gebesa.com,servicioalcliente@gebesa.com,costos@gebesa.com'
        if bom:
            cost_tot_bom = 0.000000
            for line in bom.bom_line_ids:
                cost_tot_bom += (
                    line.product_id.standard_price * line.product_qty)
            diff = product_id.standard_price - cost_tot_bom
            if abs(diff) > 20.00:
                body_mail = "<b>%s (%s):</b> \
                    <a href=http://erp.portalgebesa.com/web#id=%s&view_type=form&model=mrp.bom>%s</a> \
                    <b>%s (%s)</b>" % (
                    _('The total cost of this BoM:'),
                    str(product_id.standard_price),
                    bom.id, product_id.default_code,
                    _('is Not Equal to its Product cost!'),
                    str(cost_tot_bom))
                mail = self.env['mail.mail'].create({
                    'subject': 'Wrong Cost in BoM',
                    'email_to': email_to,
                    'headers': "{'Return-Path': u'odoo@gebesa.com'}",
                    'body_html': body_mail,
                    'auto_delete': True,
                    'message_type': 'comment',
                    'model': 'mrp.bom',
                    'res_id': bom.id,
                })
                mail.send()
                raise UserError(_(
                    'The total cost of this BoM: %s is Not Equal to its Product cost!'
                ) % product_id.default_code)

            if bom.type == 'normal' and not bom.routing_id:
                body_mail = "<b>%s:</b> \
                        <a href=web#id=%s&view_type=form&model=mrp.bom>%s \
                        </a><b>%s:</b>" % (
                            _('This BoM:'), bom.id,
                            product_id.default_code,
                            _('is for Manufacturing, but has not a Production Route!'))
                mail = self.env['mail.mail'].create({
                    'subject': 'Wrong Routing in a Production BoM',
                    'email_to': email_to,
                    'headers': "{'Return-Path': u'odoo@gebesa.com'}",
                    'body_html': body_mail + ' ' + body_mail,
                    'auto_delete': True,
                    'message_type': 'comment',
                    'model': 'mrp.bom',
                    'res_id': bom.id,
                })
                mail.send()
                raise UserError(_(
                    'This BoM: %s  is for Manufacturing, but has not a Production Route!'
                ) % product_id.default_code)

            if bom.type == 'phantom' and bom.routing_id:
                body_mail = "<b>%s:</b> \
                        <a href=web#id=%s&view_type=form&model=mrp.bom>%s \
                        </a><b>%s:</b>" % (
                            _('This BoM:'), bom.id,
                            product_id.default_code,
                            _('is a Kit, but it has a Production Route!'))
                mail = self.env['mail.mail'].create({
                    'subject': 'Wrong Routing in a Kit BoM',
                    'email_to': email_to,
                    'headers': "{'Return-Path': u'odoo@gebesa.com'}",
                    'body_html': body_mail + ' ' + body_mail,
                    'auto_delete': True,
                    'message_type': 'comment',
                    'model': 'mrp.bom',
                    'res_id': bom.id,
                })
                mail.send()
                raise UserError(_(
                    'This BoM: %s is a Kit, but it has a Production Route!'
                ) % product_id.default_code)

        res = super()._prepare_mo_vals(
            product_id=product_id, product_qty=product_qty,
            product_uom=product_uom, location_id=location_id,
            name=name, origin=origin, values=values, bom=bom)
        res['rule_id'] = self.id
        return res

    def _get_stock_move_values(self, product_id, product_qty, product_uom,
                               location_id, name, origin, values, group_id):
        res = super()._get_stock_move_values(
            product_id=product_id, product_qty=product_qty,
            product_uom=product_uom, location_id=location_id,
            name=name, origin=origin, values=values, group_id=group_id)
        if 'move_dest_ids' in values.keys():
            production = values['move_dest_ids'].raw_material_production_id
            if production:
                res['origin'] += (':' + production.name + ' ' + location_id.name)
            elif self.location_src_id.usage == 'transit':
                res['origin'] = (
                    values['move_dest_ids'].origin + '|'
                    + self.location_src_id.name + '->' + location_id.name)
            elif location_id.usage == 'transit':
                res['origin'] = (
                    values['move_dest_ids'].origin.split('|')[0]
                    + '|' + self.location_src_id.name + '->' + location_id.name)
        return res

# class ProcurementGroup(models.Model):
#     _inherit = 'procurement.group'

#     @api.model
#     def _search_rule(self, product_id, values, domain):
#         for dom in domain:
#             if dom[0] == 'location_id':
#                 location = self.env['stock.location'].browse(dom[2])
#         if location.usage == 'internal':
#             bom = self.env['mrp.bom'].search([
#                 ('product_id', '=', product_id.id),
#                 ('active', '=', True)])
#             if bom and bom.routing_id:
#                 location_dest = bom.routing_id.location_id
#                 if location.id != location_dest.id:
#                     domain = expression.AND([[
#                         ('location_src_id', '=', bom.routing_id.location_id.id)],
#                         domain])
#         return super(ProcurementGroup, self)._search_rule(
#             product_id, values, domain)
