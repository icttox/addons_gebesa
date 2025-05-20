# Copyright 2020, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def back_to_life_mo_moves(self):
        """
            vuelve a draft los moves de la MO que estuvieran cancelados
        """
        for odf in self:
            odf.move_raw_ids.filtered(lambda m: m.state == 'cancel').action_back_to_draft()
            odf.move_finished_ids.filtered(lambda m: m.state == 'cancel').action_back_to_draft()


    @api.multi
    def generate_procure_pickings(self):
        """
            crea los pickings de abastecimiento cuando no los genero
            desde que se creó la MO
        """

        # create procurements for make to order moves
        for odf in self:
            for move in odf.move_raw_ids:
                has_move_prev = move.move_orig_ids.filtered(
                    lambda m: m.state != 'cancel')
                # Prevent generate pickings more than once
                if has_move_prev:
                    continue
                values = move._prepare_procurement_values()
                origin = (move.group_id and move.group_id.name or (
                    move.origin or move.picking_id.name or "/"))
                self.env['procurement.group'].run(
                    move.product_id,
                    move.product_uom_qty,
                    move.product_uom,
                    move.location_id,
                    move.rule_id and move.rule_id.name or "/", origin,
                    values)

    @api.multi
    def generate_procure_pickings_first_level(self):
        """
            crea los pickings de abastecimiento cuando no los genero
            desde que se creó la MO
        """

        # create procurements for make to order moves
        for odf in self:
            for move in odf.move_raw_ids:
                has_move_prev = move.move_orig_ids.filtered(
                    lambda m: m.state != 'cancel')
                # Prevent generate pickings more than once
                if has_move_prev:
                    continue
                values = move._prepare_procurement_values()
                origin = (move.group_id and move.group_id.name or (
                    move.origin or move.picking_id.name or "/"))
                self.env['procurement.group'].run_only_pull_geb(
                    move.product_id,
                    move.product_uom_qty,
                    move.product_uom,
                    move.location_id,
                    move.rule_id and move.rule_id.name or "/", origin,
                    values)

    def client_server_action_geb_proc_pick(self, vals):
        # mos = self.env['mrp.production'].search(['name', 'in', (vals)])
        # for mo in mos:

        its_us = self.env.user.has_group(
            'system_administrator.group_system_administrator_gebesa')
        if not its_us:
            return
        for mo in vals:
            mpprod = self.env[
                'mrp.production'].search(
                [('name', '=', mo)], limit=1)

            if not mpprod:
                continue

            mpprod.generate_procure_pickings()
            mpprod.back_to_life_mo_moves()

    def client_server_action_geb_proc_pick_only_pull(self, vals):
        # mos = self.env['mrp.production'].search(['name', 'in', (vals)])
        # for mo in mos:

        its_us = self.env.user.has_group(
            'system_administrator.group_system_administrator_gebesa')
        if not its_us:
            return
        for mo in vals:
            mpprod = self.env[
                'mrp.production'].search(
                [('name', '=', mo)], limit=1)

            if not mpprod:
                continue

            mpprod.generate_procure_pickings_first_level()
            mpprod.back_to_life_mo_moves()


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def run_only_pull_geb(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        """ Method used in a procurement case. The purpose is to supply the
        product passed as argument in the location also given as an argument.
        In order to be able to find a suitable location that provide the product
        it will search among stock.rule.
        """
        values.setdefault('company_id', self.env['res.company']._company_default_get('procurement.group'))
        values.setdefault('priority', '1')
        values.setdefault('date_planned', fields.Datetime.now())
        rule = self._get_rule(product_id, location_id, values)
        if not rule:
            raise UserError(_('No procurement rule found in location "%s" for product "%s".\n Check routes configuration.') % (location_id.display_name, product_id.display_name))
        action = 'pull' if rule.action == 'pull_push' else rule.action
        if action != 'pull':
            return True
        rule._run_pull_geb(product_id, product_qty, product_uom, location_id, name, origin, values)
        # if hasattr(rule, '_run_%s_geb' % action):
        #     getattr(rule, '_run_%s_geb' % action)(product_id, product_qty, product_uom, location_id, name, origin, values)
        # else:
        #     _logger.error("The method _run_%s doesn't exist on the procument rules" % action)
        return True


class StockRule(models.Model):
    """ A rule describe what a procurement should do; produce, buy, move, ... """
    _inherit = 'stock.rule'

    def _run_pull_geb(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        if not self.location_src_id:
            msg = _('No source location defined on stock rule: %s!') % (self.name, )
            raise UserError(msg)

        # create the move as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
        # Search if picking with move for it exists already:
        group_id = False
        if self.group_propagation_option == 'propagate':
            group_id = values.get('group_id', False) and values['group_id'].id
        elif self.group_propagation_option == 'fixed':
            group_id = self.group_id.id

        data = self._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
        # Since action_confirm launch following procurement_group we should activate it.
        move = self.env['stock.move'].sudo().with_context(force_company=data.get('company_id', False)).create(data)
        move._action_confirm_geb()
        return True


class StockMove(models.Model):
    _inherit = 'stock.move'
    def _action_confirm_geb(self, merge=True, merge_into=False):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        :param: merge: According to this boolean, a newly confirmed move will be merged
        in another move of the same picking sharing its characteristics.
        """
        move_create_proc = self.env['stock.move']
        move_to_confirm = self.env['stock.move']
        move_waiting = self.env['stock.move']

        to_assign = {}
        for move in self:
            # if the move is preceeded, then it's waiting (if preceeding move is done, then action_assign has been called already and its state is already available)
            if move.move_orig_ids:
                move_waiting |= move
            else:
                if move.procure_method == 'make_to_order':
                    move_create_proc |= move
                else:
                    move_to_confirm |= move
            if move._should_be_assigned():
                key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)
                if key not in to_assign:
                    to_assign[key] = self.env['stock.move']
                to_assign[key] |= move

        # create procurements for make to order moves
        # for move in move_create_proc:
            # values = move._prepare_procurement_values()
            # origin = (move.group_id and move.group_id.name or (move.origin or move.picking_id.name or "/"))
            # self.env['procurement.group'].run(move.product_id, move.product_uom_qty, move.product_uom, move.location_id, move.rule_id and move.rule_id.name or "/", origin,
            #                                  values)

        move_to_confirm.write({'state': 'confirmed'})
        (move_waiting | move_create_proc).write({'state': 'waiting'})

        # assign picking in batch for all confirmed move that share the same details
        for moves in to_assign.values():
            moves._assign_picking()
        #self._push_apply()
        if merge:
            return self._merge_moves(merge_into=merge_into)
        return self
