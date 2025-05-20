# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BomMassiveImport(models.Model):
    _name = 'bom.massive.import'
    _description = 'Bom Massive Import'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.multi
    def get_state_massive(self):
        if self.action == 'update':
            self.update_bom_massive()
        elif self.action == 'add':
            self.insert_bom_massive()
        elif self.action == 'delete':
            self.delete_bom_massive()
        else:
            raise ValidationError("Invalid value for 'action' field")

    name = fields.Char(
        string='Code',
        size=64,
    )

    date = fields.Date(
        string='Date',
        default=fields.Date.today,
    )

    action = fields.Selection(
        [('update', 'Update'),
         ('add', 'Add'),
         ('delete', 'Delete')],
        string='Action',
        default='update',
    )

    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done')],
        string='State',
        default='draft',
    )

    lines_ids = fields.One2many(
        'bom.massive.import.line',
        'bom_massive_id',
        string='Bom Massive lines',
    )

    location_id = fields.Many2one(
        'stock.location',
        string='Stock Location',
    )

    @api.multi
    def update_bom_massive(self):
        product_obj = self.env['product.product']
        bom_obj = self.env['mrp.bom']
        bom_line_obj = self.env['mrp.bom.line']

        for massive in self:
            done_ids = []

            if massive.location_id:
                raise ValidationError(_('The Warehouse is Wrong'))

            for line in massive.lines_ids:

                prod_master = product_obj.with_context(
                    active_test=False).search([
                        ('default_code', '=', line.code_master),
                        # ('active', '=', True)
                    ])
                # No existe el producto padre
                if not prod_master:
                    message = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (
                        _("Clave Incorrecta Padre"), line.code_master)
                    massive.message_post(body=message)
                    continue

                # No existe el producto detalle actual
                prod_old = product_obj.with_context(
                    active_test=False).search([
                        ('default_code', '=', line.code_current),
                        # ('active', '=', True)
                    ])
                if not prod_old:
                    message = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (
                        _("Current Incorrect Key"), line.code_current)
                    massive.message_post(body=message)
                    continue

                # No existe el producto detalle Nuevo
                prod_new = product_obj.search(
                    [('default_code', '=', line.code_update),
                     ('active', '=', True)])
                if not prod_new:
                    message = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (
                        _("Incorrect Key to Update"), line.code_update)
                    massive.message_post(body=message)
                    continue

                # El producto detalle Nuevo no puede ser igual al producto padre
                if prod_new.id == prod_master.id:
                    message = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (
                        _("Is the same code to update"), line.code_update)
                    massive.message_post(body=message)
                    continue

                # Buscamos si el producto padre tiene lista de materiales
                bom_ids = bom_obj.with_context(
                    active_test=False).search([
                        ('product_id', '=', prod_master.id),
                        ('bom_line_ids', '!=', False)])
                if not bom_ids:
                    message = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (
                        _("Product has no valid path"), prod_master.default_code)
                    massive.message_post(body=message)
                    continue

                for bom in bom_ids:

                    # Buscamos si existe un BoM line para el producto actual
                    bom_line_old_prod = bom_line_obj.search(
                        [('bom_id', '=', bom.id),
                         ('product_id', '=', prod_old.id)], limit=1)
                    if not bom_line_old_prod:  # sale_order_ok_etl
                        message = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (
                            _("The following product does not contain a correct BoM"),
                            line.code_master)
                        massive.message_post(body=message)
                        continue

                    # validacion para cuando el update ya existe
                    bom_line_new_prod = bom_line_obj.search(
                        [('product_id', '=', prod_new.id),
                         ('bom_id', '=', bom.id)])

                    if bom_line_new_prod and (prod_old.id != prod_new.id):
                        message = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (
                            _("Code exists in this bom"), line.code_update)
                        massive.message_post(body=message)
                        continue

                    for line_id in bom.bom_line_ids:
                        if line_id.product_id.id == prod_new.id and prod_old.id != prod_new.id:
                            message = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (
                                _("This product is already in the BoM"), line.code_update)
                            massive.message_post(body=message)
                            continue

                    # El producto a actualizar es el mismo que el actual
                    # Se comentaria esta validacion supongamos que el usuario
                    # solo desea actualizar cantidad y para ello pone la misma clave
                    # tanto en el producto actual como el anterior
                    # if line.code_current == line.code_update:
                    #     message_body_line = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (_("Must be different Keys"), line.code_update)
                    #     massive.message_post(body=message_body_line)
                    #  .   continue

                    # La cantidad nueva no puede ser igual o menor que cero
                    if line.cantidad_import <= 0:
                        message = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (
                            _("Can not have Quantity 0"), line.code_update)
                        massive.message_post(body=message)
                        continue

                    if bom.type == 'phantom':
                        bom_id = bom_obj.search(
                            [('product_id', '=', prod_new.id),
                             ('active', '=', True)])
                        if not bom_id:
                            message = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (
                                _("The following product must have List Materials"),
                                line.code_update)
                            massive.message_post(body=message)
                            continue
                    # asignar
                    bom_line_old_prod.product_qty = line.cantidad_import
                    bom_line_old_prod.product_id = prod_new.id
                    bom_line_old_prod.product_uom_id = prod_new.uom_id.id

                    if bom.id in done_ids:
                        continue
                    if not bom.active or not prod_master.active:
                        continue
                    done_ids.append(bom.id)

            # Revaluacion
            for bom in done_ids:
                self.env['mrp.bom'].browse(bom).action_reval()

            massive.state = 'done'

    @api.multi
    def insert_bom_massive(self):
        product_mas_obj = self.env['product.product']
        bom_obj = self.env['mrp.bom']
        bom_line_obj = self.env['mrp.bom.line']
        # loc_obj = self.env['stock.location']

        for massive in self:
            done_ids = []
            if not massive.location_id:
                raise ValidationError(_('Need Warehouse'))
            for line in massive.lines_ids:

                # Buscamos producto maestro
                prod = product_mas_obj.search(
                    [('default_code', '=', line.code_master),
                     ('active', '=', True)])
                if not prod:  # sale_order_ok_etl
                    message_body = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (_("Incorrect Parent Key"), line.code_master)
                    massive.message_post(body=message_body)
                    continue
                # Buscamos producto a insertar en el detalle
                prod3 = product_mas_obj.search(
                    [
                        ('default_code', '=', line.code_update),
                        ('active', '=', True)
                    ])
                if not prod3:  # sale_order_ok_etl
                    message_body3 = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (_("Incorrect Key to Update"), line.code_update)
                    massive.message_post(body=message_body3)
                    continue

                if line.cantidad_import <= 0:  # validacion para la cantidad
                    message_body_line = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (_("The quantity dont have 0"), line.code_update)
                    massive.message_post(body=message_body_line)
                    continue

                # Un producto no se puede contener a sí mismo
                if prod3.id == prod.id:  # validacion para que no sean igual
                    message_body3 = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (_("Is the same code update"), line.code_update)
                    massive.message_post(body=message_body3)
                    continue

                # BoM del producto maestro
                bomm = bom_obj.search([('product_id', '=', prod.id),
                                       ('active', '=', True)])
                if not bomm.product_id:
                    message_body_bomm = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (_("The following product does not contain a BoM"),line.code_update)
                    massive.message_post(body=message_body_bomm)
                    continue

                # validacion para cuando el update ya existe
                bommerror = bom_line_obj.search(
                    [('product_id', '=', prod3.id),
                     ('bom_id', '=', bomm.id)])
                if bommerror:
                    message_body_line = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (_("Code exists in this bom"), line.code_update)
                    massive.message_post(body=message_body_line)
                    continue

                # Buscamos la ubicacion MP del almacén del bom
                if massive.location_id.stock_warehouse_id.id != bomm.warehouse_id.id:
                    message_body_line = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (_("The Location not is the type"), line.code_update)
                    massive.message_post(body=message_body_line)
                    continue

                for bom_line in bomm.bom_line_ids:
                    if bom_line.product_id.id == prod3.id:
                        message_body_line = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (_("This product is already in the BoM"), line.code_update)
                        massive.message_post(body=message_body_line)
                        continue

                # Tipo Phantom
                if bomm.type == 'phantom':
                    # BoM del articulo a insertar
                    bom_phantom = bom_obj.search(
                        [('product_id', '=', prod3.id),
                         ('active', '=', True)])
                    if not bom_phantom:
                        message_body_line = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (_("The following product must have List Materials"), line.code_update)
                        massive.message_post(body=message_body_line)
                        continue
                # Creacion del diccionario
                line_vals = {
                    'product_id': prod3.id,
                    'bom_id': bomm.id,
                    'product_qty': line.cantidad_import,
                    'product_uom': prod3.product_tmpl_id.uom_id.id,
                    'location_id': massive.location_id.id,
                    'product_uom_id': prod3.uom_id.id
                }
                bom_line_obj.create(line_vals)
                line.bom_id = prod3.id

                if bomm.id in done_ids:
                    continue
                done_ids.append(bomm.id)

            # Revaluacion
            for bom in done_ids:
                self.env['mrp.bom'].browse(bom).action_reval()
            massive.state = 'done'

    @api.multi
    def delete_bom_massive(self):
        product_obj = self.env['product.product']
        bom_obj = self.env['mrp.bom']
        bom_line_obj = self.env['mrp.bom.line']

        for massive in self:
            # Verificamos que tenga una ubicacion de existencia
            if not massive.location_id:
                raise ValidationError(_('Need Warehouse'))

            done_ids = []

            for line in massive.lines_ids:
                prod_master = product_obj.search([
                    ('default_code', '=', line.code_master),
                    ('active', '=', True)])
                # No existe el producto padre
                if not prod_master:
                    message = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (
                        _("Incorrect parent key"), line.code_master)
                    massive.message_post(body=message)
                    continue

                # No existe el producto detalle actual
                prod_dele = product_obj.search([
                    ('default_code', '=', line.code_update),
                    ('active', '=', True)])
                if not prod_dele:
                    message = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (
                        _("Incorrect key to delete"), line.code_update)
                    massive.message_post(body=message)
                    continue

                # Buscamos si el producto padre tiene lista de materiales
                bomm_id = bom_obj.search([
                    ('product_id', '=', prod_master.id),
                    ('bom_line_ids', '!=', False)])
                if not bomm_id:
                    message = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (
                        _("The parent product does not have a BOM"), prod_master.default_code)
                    massive.message_post(body=message)
                    continue

                if massive.location_id.stock_warehouse_id.id != bomm_id.warehouse_id.id:
                    message = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (_("The Location not is the type"), line.code_update)
                    massive.message_post(body=message)
                    continue

                for bom in bomm_id:
                    # Buscamos si existe un BoM line para el producto actual
                    bom_line_dele_prod = bom_line_obj.search(
                        [('bom_id', '=', bom.id),
                         ('product_id', '=', prod_dele.id)], limit=1)
                    if not bom_line_dele_prod:
                        message = "<b>%s:</b><b view_type=form&model=mrp.bom>%s</b>" % (
                            _("The product to remove from the BOM item does not exist"),
                            line.code_update)
                        massive.message_post(body=message)
                        continue

                    # Eliminar la línea del BoM
                    bom_line_dele_prod.unlink()

                    if bom.id in done_ids:
                        continue
                    done_ids.append(bom.id)

            # Revaluación
            for bom in done_ids:
                self.env['mrp.bom'].browse(bom).action_reval()
            massive.state = 'done'


class BomMassiveImportLine(models.Model):
    _name = 'bom.massive.import.line'
    _description = 'Bom Massive Import Line'

    bom_massive_id = fields.Many2one(
        'bom.massive.import',
        string='Bom Massive Import',
        ondelete='cascade',
        index=2,
        required=True,
    )

    code_master = fields.Char(
        string='Code Master',
        required=True,
    )

    code_current = fields.Char(
        string='Current Code',
    )

    code_update = fields.Char(
        string='Update Code',
        required=True,
    )

    cantidad_import = fields.Float(
        string="New Quantity",
        required=True,
    )
