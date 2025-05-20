# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import api, models
from odoo.exceptions import ValidationError
import xmlrpc.client


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    uom_dic = {
        'ACTIVIDAD': 'Activity',
        'Caja': 'Caja',
        'cm': 'cm',
        'Conjunto': 'Conjunto',
        'dm2': 'dm²',
        'pie(s)': 'ft',
        'galón(es)': 'gal (US)',
        'Hoja': 'Hoja',
        'Hora(s)': 'Hours',
        'Cientos': 'Cientos',
        'pulgada(s)': 'in',
        'kg': 'kg',
        'Kilowatt': 'Kilowatt',
        'Kit': 'Kit',
        'Litro(s)': 'L',
        'm': 'm',
        'm2': 'm²',
        'm3': 'm³',
        'Modulo': 'Modulo',
        'Paquete': 'Paquete',
        'Pieza': 'Pieza',
        'Rollo': 'Rollo',
        'Servicio': 'Servicio',
        'Servicio Flete': 'Servicio Flete',
        'Juego': 'Juego',
        'Tramo': 'Tramo',
        'Unidad(es)': 'Units',
    }

    def _get_connection(self):
        url = self.env['ir.config_parameter'].sudo().get_param('gebesa_integracion_odoo.inter_odoo_url', 'False')
        db = self.env['ir.config_parameter'].sudo().get_param('gebesa_integracion_odoo.inter_odoo_db', 'False')
        username = self.env.user.partner_id.inter_odoo_user
        password = self.env.user.partner_id.inter_odoo_pass

        if not url:
            raise ValidationError("Please specify a odoo url")
        if not db:
            raise ValidationError("Please specify a odoo database")
        if not username:
            raise ValidationError("Please specify a odoo user")
        if not password:
            raise ValidationError("Please specify a odoo password")

        return (url, db, username, password)

    @api.multi
    def send_product_odoo(self):
        url, db, username, password = self._get_connection()
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        if not uid:
            raise ValidationError("Could not authenticate in Odoo 16.")

        for product in self:
            # verificamos que no exista la clave
            if product.default_code:
                existing_product = models.execute_kw(
                    db, uid, password, 'product.template', 'search',
                    [[['default_code', '=', product.default_code]]])
                if existing_product:
                    raise ValidationError("A product already exists in odoo with the key '{}'.".format(product.default_code))

            # verificamos que exista la unidad de medida
            existing_uom = models.execute_kw(
                db, uid, password, 'uom.uom', 'search',
                [[['name', '=', self.uom_dic[product.uom_id.name]]]])
            if not existing_uom:
                raise ValidationError("The unit of measure with the name does not exist '{}'.".format(product.uom_id.name))

            # verificamos que exista la familia
            if product.family_id:
                model, family_id = models.execute_kw(
                    db, uid, password, 'ir.model.data', 'check_object_reference',
                    ['__import__', 'mpf_prod_fam_' + str(product.family_id.id)])
                if not family_id:
                    raise ValidationError("The family '{}' does not exist in Odoo.".format(product.family_id.name))
            else:
                family_id = False

            # verificamos que exista el grupo
            if product.group_id:
                model, group_id = models.execute_kw(
                    db, uid, password, 'ir.model.data', 'check_object_reference',
                    ['__import__', 'mpf_prod_group_' + str(product.group_id.id)])
                if not group_id:
                    raise ValidationError("The group '{}' does not exist in Odoo.".format(product.group_id.name))
            else:
                group_id = False

            # verificamos que exista la linea del producto
            if product.line_id:
                model, line_id = models.execute_kw(
                    db, uid, password, 'ir.model.data', 'check_object_reference',
                    ['__import__', 'mpf_prod_line_' + str(product.line_id.id)])
                if not line_id:
                    raise ValidationError("The line '{}' does not exist in Odoo.".format(product.line_id.name))
            else:
                line_id = False

            # verificamos que exista el tipo del producto
            if product.type_id:
                model, type_id = models.execute_kw(
                    db, uid, password, 'ir.model.data', 'check_object_reference',
                    ['__import__', 'mpf_prod_type_' + str(product.type_id.id)])
                if not type_id:
                    raise ValidationError("The type '{}' does not exist in Odoo.".format(product.type_id.name))
            else:
                type_id = False

            # Crea un registro en Odoo 16
            product_data = {
                'default_code': product.default_code,
                'name': product.name,
                'detailed_type': product.type,
                'standard_price': product.standard_price,
                'uom_id': existing_uom[0],
                'family_id': family_id,
                'group_id': group_id,
                'is_line': product.is_line,
                'line_id': line_id,
                'type_id': type_id,
                'type_product': product.type_product,
            }
        models.execute_kw(db, uid, password, 'product.template', 'create', [product_data])
