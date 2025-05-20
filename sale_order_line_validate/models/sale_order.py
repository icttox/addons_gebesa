# Copyright 2020, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
from odoo.exceptions import UserError, ValidationError
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[('validation_process', 'In validation process')])

    def _get_forbidden_state_confirm(self):
        res = super()._get_forbidden_state_confirm()
        res.add('validation_process')
        return res

    @api.multi
    def write(self, values):
        for order in self:
            if 'segment_status' in values.keys():
                if order.state == 'validation_process':
                    raise UserError(
                        'El pedido %s esta en proceso de validacion' % (
                            order.name))
        return super().write(values)

#     @api.multi
#     def validate_lines_by_lots(self, numlines):

#         for order in self:
#             lines_to_validate = self.env['sale.order.line'].search([
#                 ('order_id', '=', order.id),
#                 ('validated', '=', False),
#                 ('state', 'not in', ['cancel', 'done', 'closed'])], limit=numlines)
#             lines_to_validate.validate_line()

    @api.multi
    def perform_orders_validations(self):
        for order in self:
            if order.company_id.is_manufacturer:
                if not order.qty_attachments or order.qty_attachments == 0:
                    raise UserError(_('You need to attach a Purchase Order!'))

                if not order.order_line:
                    raise UserError(_('You cannot confirm a sales order which has \
                    no line.'))

                for lines in order.order_line:
                    if lines.product_id.type == 'cotiza':
                        raise ValidationError(_(
                            'This product is type quotation: %s,  not cant \
                            Validate this Sale Order') % (lines.product_id.name))

                    if lines.product_id.type == 'service':
                        continue
                    if lines.price_unit <= 0:
                        raise UserError(_('At least one of the lines of the \
                        sale order has price unit zero!' '\n Please make sure \
                        that all lines have successfully captured the unit price.')
                                        )

                    if not lines.route_id:
                        raise UserError(
                            _('Product line %s does not have a route assigned'
                              % (lines.product_id.default_code)))
                    if lines.standard_cost == 0.00:
                        raise UserError(
                            "No se puede validar un producto con costo 0 (%s)"
                            % (lines.product_id.default_code))

                    cantidad_ped = lines.product_uom_qty
                    product_ped = lines.product_id.sale_product_quantity
                    product_ped = float(product_ped)
                    if cantidad_ped < product_ped and cantidad_ped > 0:
                        raise UserError(
                            ("La cantidad minima a vender del producto: %s es: %s" % (lines.product_id.default_code,product_ped)))
                    if product_ped > 0 and cantidad_ped >= product_ped:
                        resto = cantidad_ped % product_ped
                        if resto != 0:
                            raise UserError(_("Este producto solo puede vender multiplos de %s") % product_ped)

                resws2 = order.product_data_validation2()

                if resws2 != 'OK':
                    raise ValidationError('Este pedido no podra ser aprobado  \
                        debido a errores de configuracion \
                        en los productos que ocasionarian \
                        excepciones, se ha enviado un correo detallado a los \
                        interesados.')

                order.validate_manufacturing()
                if not order.notify_approval:
                    raise UserError(
                        _('The following field is not invalid:\nNotify approval'))
                if not order.manufacture:
                    raise UserError(
                        _('The following field is not invalid:\nManufacture'))
                if not order.priority:
                    raise UserError(
                        _('The following field is not invalid:\nManufacturing \
                          priority'))
                if not order.analytic_account_id:
                    raise UserError(
                        _('The following field is not invalid:\nAnalytic Account'))
                if not order.client_order_ref:
                    raise UserError(_('This Sale Order not has OC captured'))
                if not order.date_reception:
                    raise UserError(_('This Sale Order not has Date Reception'))
                if order.warehouse_id != order.analytic_account_id.warehouse_id:
                    raise UserError(
                        ('No coincide la Analítica con el almacen seleccionado'))

            order.write({
                'state': 'validation_process',
                'confirmation_date': fields.Datetime.now()})
            order.calculate_profit_margin()

    @api.multi
    def post_validation_order(self):

        order_ids = self.search([('state', '=', 'validation_process')])

        for order in order_ids:
            line_ids = self.env['sale.order.line'].search([
                ('order_id', '=', order.id),
                ('revalidated', '!=', True)], order='id', limit=50)
            self._cr.execute("""UPDATE sale_order_line SET revalidated= True
                WHERE id IN %s""", [tuple(line_ids.ids)])

            _logger.error(
                _('so line validation: %s comienza' % order.name))
            line_ids.re_validate_line(is_revalidate=False)
            _logger.error(
                _('so line validation: %s termina' % order.name))

            if any(not line.revalidated for line in order.order_line):
                continue

            order.action_done()
            # order.force_quotation_send()

            if order.pricelist_id.currency_id.name == 'MXN' and \
               order.amount_total >= 200000 or \
               order.pricelist_id.currency_id.name == 'USD' and \
               order.amount_total >= 10000:
                body_mail = "<b>%s</b> \
                            <a href=web#id=%s&view_type=form&model=sale.order>%s</a> \
                            <b>%s:</b> \
                            <a href=web#id=%s&view_type=form&model=res.partner>%s</a> \
                            <b>%s %s %s.</b>" % (_('Se validó un Pedido de Venta'),
                                                 order.id, order.name,
                                                 _('del Cliente'),
                                                 order.partner_id.id,
                                                 order.partner_id.name,
                                                 _('con un Monto Total de $'),
                                                 order.amount_total,
                                                 order.pricelist_id.currency_id.name)

                mail = self.env['mail.mail'].create({
                    'subject': 'Re:' + order.name,
                    'email_to': 'equipocompras@gebesa.com,sistemas@gebesa.com,sebastian@gebesa.com,programacion@gebesa.com,cristina.rodriguez@gebesa.com',
                    'headers': "{'Return-Path': u'odoo@gebesa.com'}",
                    'body_html': body_mail,
                    'auto_delete': True,
                    'message_type': 'comment',
                    'model': 'sale.order',
                    'res_id': order.id,
                })
                mail.send()
            order.order_line.write({'revalidated': False})

        # for order in self:
        #     order.write({'state': 'validation_process'})
        #     if any(not line.validated for line in order.order_line):
        #         continue

        #     dealer = order.partner_dealer_id.id or False
        #     if dealer:
        #         self._cr.execute('UPDATE mrp_production mp SET partner_dealer_id = %s '
        #                          'FROM procurement_group pg '
        #                          'WHERE pg.sale_id = %s AND pg.id = mp.procurement_group_id',
        #                          (dealer, order.id,))


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # state = fields.Selection(
    #     selection_add=[('validation_process', 'In validation process')])

    revalidated = fields.Boolean(
        string='Re-Validated',
        help='Indicate if this sale order line was closed and re-validated'
    )

    @api.multi
    def re_validate_line(self, is_revalidate=True):
        ''' Validate by sale order line
            needed specially in large orders
        '''

        for line in self:
            if line.revalidated and is_revalidate == True:
                continue
            # line.order_id.perform_orders_validations()
            line.perform_line_validations()
            # line.order_id.write({'state': 'sale', 'confirmation_date': fields.Date.today()})
            line.write({'state': 'sale'})
            _logger.error(
                _('so line validation: %s comienza linea' % line.product_id.default_code))
            line._action_launch_stock_rule()
            _logger.error(
                _('so line validation: %s termina linea launch stock rule' % line.product_id.default_code))
            line.post_validation_line()
            _logger.error(
                _('so line validation: %s termina linea post line validation' % line.product_id.default_code))
            # line.order_id.post_validation_order()

    @api.multi
    def perform_line_validations(self):
        for line in self:
            if line.product_id:
                if line.product_id.type == 'service':
                    continue
                if line.product_id.type == 'cotiza':
                    raise ValidationError(_(
                        'This product is type quotation: %s, can\'t be validated') % (line.product_id.default_code))

                if not line.route_id:
                    raise UserError(
                        _('Product line %s does not have a route assigned'
                          % (line.product_id.default_code)))
                if line.standard_cost == 0.00:
                    raise UserError(
                        "No se puede validar un producto con costo 0 (%s)"
                        % (line.product_id.default_code))
                routes = line.product_id.route_ids + \
                    line.product_id.categ_id.total_route_ids
                if len(routes) < 2:
                    raise UserError(
                        _('%s %s %s' % (
                            _("The next product has no a valid Route"),
                            line.product_id.default_code,
                            line.product_id.name)))
                product_bom = False
                for bom in line.product_id.product_tmpl_id.bom_ids:
                    if bom.product_id.id == line.product_id.id:
                        product_bom = bom or False
                if not product_bom:
                    raise UserError(
                        _('%s %s %s' % (
                            _("The next product has not a Bill of Materials"),
                            line.product_id.default_code, line.product_id.name)))
                # Cantidades mínimas de venta
                cantidad_ped = line.product_uom_qty
                product_ped = float(line.product_id.sale_product_quantity)
                if cantidad_ped < product_ped and cantidad_ped > 0:
                    raise UserError(
                        ("La cantidad minima a vender del producto: %s es: %s" % (line.product_id.default_code,product_ped)))
                if product_ped > 0 and cantidad_ped >= product_ped:
                    resto = cantidad_ped % product_ped
                    if resto != 0:
                        raise UserError(_("Este producto solo puede vender multiplos de %s") % product_ped)
                if line.price_unit <= 0:
                    raise UserError(_('At least one of the lines of the \
                    sale order has price unit zero!' '\n Please make sure \
                    that all lines have successfully captured the unit price.'))

    @api.multi
    def post_validation_line(self):

        for line in self:
            line.write({'revalidated': True,
                        'state': 'done',
                        'closed': False})
            line.order_id.write({
                'sale_everywhere': False
            })
