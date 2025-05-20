# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import api, fields, _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    old_bom_dynamic = fields.Boolean(
        string='Old Bom Dynamic',
    )
    is_bom_dynamic = fields.Boolean(
        string='Is BOM Dynamic',
    )

    @api.model
    def delete_bom_dynamic_inactive(self):
        self._cr.execute("""
            DELETE FROM mrp_bom_line WHERE bom_id IN (
                SELECT id FROM mrp_bom WHERE old_bom_dynamic IS TRUE
                AND active IS FALSE ORDER BY id LIMIT 5)
            """)
        self._cr.execute("""
            DELETE FROM mrp_bom WHERE id IN (
                SELECT id FROM mrp_bom WHERE old_bom_dynamic IS TRUE
                AND active IS FALSE ORDER BY id LIMIT 5)
            """)

    @api.multi
    def action_propagar(self):
        # Declaracion de objetos
        multiequiv_pos = 0
        product_obj = self.env['product.product']
        bom_obj = self.env['mrp.bom']
        bml_obj = self.env['mrp.bom.line']
        attribute_obj = self.env['mrp.bom.line.detail.attribute']
        equivalent_obj = self.env['product.attribute.value.equivalent']
        # Template del producto del BoM Actual
        templ = self.product_tmpl_id
        global_product_values = []
        new_boms = []
        cant_factor_uno = 0
        # Verifica que las otras variantes no tengan lineas de remplazo
        bom_remplace = bom_obj.search([
            ('active', '=', True),
            ('product_tmpl_id', '=', templ.id),
            ('product_id', '!=', self.product_id.id)])
        line_replace = bom_remplace.mapped('bom_line_ids').mapped(
            'bom_line_product_value_ids')
        if line_replace:
            raise UserError(
                _('One or more lists of materials have replacement lines.\n \
                   please make sure you are propagating the correct bill of materials'))
        # Consulta el BoM actual, Template y variante de producto
        # BoM Original o fuente
        bom_source = bom_obj.search([
            ('active', '=', True),
            ('product_tmpl_id', '=', templ.id),
            ('product_id', '=', self.product_id.id)])

        # Si no existe un BoM Original con los datos de producto
        # pasados marca error
        if not bom_source:
            raise UserError(
                _('The source BoM does not exist or is not active'))

        # Si la variante de producto tiene BoM duplicado
        # marca error
        if len(bom_source) > 1:
            raise UserError(_('This product exists in various BoMs'))

        # Trae las variantes (product.product) del product template origen
        product_products = templ.product_variant_ids.filtered(
            lambda pro_pro: pro_pro.active and pro_pro.id != self.product_id.id)

        # Guarda todas las lineas de detalle de reemplazo
        for replacement in self.bom_line_ids.mapped('bom_line_product_value_ids'):
            global_product_values.append(replacement)

        # Inactiva y marca para eliminar los bom anteriores
        self._cr.execute("""
            UPDATE mrp_bom SET active = FALSE,
                old_bom_dynamic = TRUE
            WHERE active IS TRUE
                AND product_tmpl_id = %s
                AND product_id IN %s
            """, (templ.id, tuple(product_products.ids)))

        # Recorre las variantes de producto del template origen
        # product.product
        for product_variant_actual in product_products:
            # Crea una copia del BoM origen
            bom_new_copy = bom_source.with_context(
                bom_dynamic=True).action_copy_cut_detail()

            new_boms.append(bom_new_copy)

            # Reemplaza la variante del producto en la nueva copia del BoM
            # Aun no se aplica el cambio por que el ORM hace el commit
            # Hasta el final de la transaccion
            bom_new_copy.with_context(bom_dynamic=True).write({
                'product_id': product_variant_actual.id,
                'is_bom_dynamic': True})

            # Consulta el (los) id(s) de los atributos que dio origen a la
            # variante de producto anterior (NO la nueva copia del BoM)
            # Esto por que la consulta se hace por SQL, esta consultando
            # el valor anterior toda ves que el ORM aun no aplica el
            # cambio de producto
            # TCase: Que pasa si mas de un valor dieron origen a la
            # variante del Producto
            self._cr.execute(
                """SELECT pav.id
                FROM product_attribute_value_product_product_rel as rel
                LEFT JOIN product_attribute_value
                as pav ON (pav.id = rel.product_attribute_value_id)
                WHERE rel.product_product_id = %s ORDER BY pav.id""",
                ([bom_new_copy.product_id.id]))

            # Si trae al menos un id de valor de variante:
            # guarda el primero en la variable primero
            attvalues_product_bom = False
            if self._cr.rowcount:
                # Guarda en un tuple todos los ids de valores de atributos
                # que dieron lugar al producto del BoM
                attvalues_product_bom = [r[0] for r in self._cr.fetchall()]
                # attvalues_product_bom = self._cr.fetchone()

            attvalues_product_bom_equiv = []
            for attval in attvalues_product_bom:
                # _logger.error('Aqui empieza: %s' % product_variant_actual.default_code)
                pva_default_code = product_variant_actual.default_code

                valseq = values_equiv = equivalent_obj.search([
                    ('value_origin_id', '=', attval)]).filtered(
                        lambda x: x.value_id.attribute_code in pva_default_code)

                if len(valseq) > 1:
                    values_equiv = values_equiv[multiequiv_pos].value_id.id
                    multiequiv_pos += 1
                    # raise UserError(
                    #    _("There is an abnormal condition, this product has duplicated variant equivalent"))
                else:
                    values_equiv = values_equiv.value_id.id

                # _logger.error(values_equiv)
                if values_equiv:
                    attvalues_product_bom_equiv.append(
                        values_equiv)
                    # _logger.error('If')
                else:
                    attvalues_product_bom_equiv.append(
                        attval)
                    # _logger.error('Else')

            # Guarda en una variable las lineas del BoM recien creado
            # new_bomlines = bom_new_copy.bom_line_ids
            new_line_change = []
            # Recorre cada linea del nuevo BoM
            for new_line in bom_new_copy.bom_line_ids:
                # Verifica si la linea es fija
                # _logger.error("Producto padre: %s" % str(bom_new_copy.product_id.default_code))
                # _logger.error("Producto boml: %s" % str(new_line.product_id.default_code))
                # _logger.error("linea fija: %s" % str(new_line.fixed))
                if new_line.fixed:
                    prev_bomline = bml_obj.search(
                        [('product_id', '=', new_line.product_id.id),
                         ('bom_id', '=', bom_source.id)], limit=1)
                    mbl_src = prev_bomline[0]
                    # _logger.error("mbl_src: %s" % str(mbl_src.id))
                    for corte in mbl_src.bom_line_detail_ids:
                        # _logger.error("corte: %s" % str(corte.name))
                        # _logger.error("Newline ID: %s" % str(new_line.id))
                        corte_copy = corte.copy({
                            'bom_line_id': new_line.id, 'color_id': False})
                        corte_copy.write(
                            {'bom_line_id': new_line.id})
                    continue
                # Si el template de la nueva linea de BoM tiene
                # Reference Mask (Tiene variantes)
                # PROPAGACION POR VARIANTES
                bom_sourse_line_remplace = bml_obj.search([
                    ('bom_id', '=', bom_source.id),
                    ('product_id', '=', new_line.product_id.id)])
                # if new_line.product_id.id == 1614959:
                #     import ipdb; ipdb.set_trace()
                if not bom_sourse_line_remplace.bom_line_product_value_ids:
                    # Consulta el Factor de la(s) variante(s) que dio
                    # origen a la variante de producto en la linea
                    # de BoM actual (original)
                    # TCase: Tal vez de error cuando traiga mas de
                    # una variante relacionada al product_product
                    # realizar pruebas con GBS110

                    # Para el calculo de la nueva cantidad
                    # Solo tomará en cuenta el primer valor de
                    # atributo con factor, se ignorarán los
                    # demás
                    self._cr.execute(
                        """SELECT pav.attribute_id, pav.factor
                        FROM product_attribute_value_product_product_rel
                         as rel
                        JOIN product_attribute_value AS pav
                         ON (pav.id = rel.product_attribute_value_id)
                        WHERE rel.product_product_id = %s ORDER BY pav.id LIMIT 1""",
                        ([new_line.product_id.id]))

                    # Si trae al menos un id de valor de variante:
                    factor_original = False
                    id_factor = False
                    if self._cr.rowcount:
                        # Guarda el factor del primer valor que encontró
                        out_value = self._cr.fetchone()
                        id_factor = out_value[0]
                        factor_original = out_value[1]

                        # Si el producto de la nueva linea de BoM
                        # tiene cantidad diferente de cero
                        if new_line.product_qty != 0:
                            # Si en la variable tenemos
                            # algún factor guardado
                            if factor_original:
                                # Si el factor es diferente de cero
                                if factor_original != 0:
                                    # Obtenemos la cantidad a factor 1.0
                                    # del producto dividiendo la
                                    # cantidad original sobre el factor
                                    # original
                                    cant_factor_uno = \
                                        new_line.product_qty / \
                                        factor_original
                                else:
                                    # Si el factor original es cero
                                    # la cantidad a factor uno va a ser
                                    # igual a la cantidad anterior
                                    cant_factor_uno = new_line.product_qty
                            else:
                                # Si no se encontró ningun factor
                                # la cantidad a factor uno va a ser igual
                                # a la cantidad anterior
                                cant_factor_uno = \
                                    new_line.product_qty
                        else:
                            # Si detecta cantidad original igual
                            # a cero marca error
                            raise UserError(
                                _("The quantity in the BoM line can not be zero"))

                    tmpl_bomline_actual = \
                        new_line.product_id.product_tmpl_id.id

                    # Consulta los product variant del template del
                    # producto de la linea de BoM actual
                    variants_tmpl_bomline = product_obj.search(
                        [('active', '=', True),
                         ('product_tmpl_id', '=', tmpl_bomline_actual),
                         ('active', '=', True)])

                    product_prev_id = new_line.product_id.id

                    # Recorre los product.product del product template
                    # del product.product de la linea actual
                    for prod in variants_tmpl_bomline:
                        # Consulta el id del (los) valores de atributo
                        # que originaron esta variante de producto
                        self._cr.execute(
                            """SELECT pav.id
                            FROM product_attribute_value_product_product_rel
                            as rel
                            JOIN product_attribute_value AS pav
                            ON (pav.id = rel.product_attribute_value_id)
                            WHERE rel.product_product_id = %s ORDER BY pav.id""", ([prod.id]))

                        # Si hay al menos un valor de atributo relacionada
                        # a la variante de producto actual
                        values_compare = False
                        if self._cr.rowcount:
                            # Guarda en un tuple, los ids de valores
                            # de atributo que encontro en la consulta SQL
                            values_compare = [r[0] for r in self._cr.fetchall()]
                            # values_compare = self._cr.fetchone()
                            if (attvalues_product_bom == values_compare) or \
                                    all(val in attvalues_product_bom for val in values_compare) or \
                                    all(val in attvalues_product_bom_equiv for val in values_compare):
                                new_line_product_dup = bml_obj.search([
                                    ('product_id', '=', prod.id),
                                    ('bom_id', '=', bom_new_copy.id),
                                    ('id', 'in', new_line_change)],
                                    order="id asc", limit=1)
                                # if new_line_product_dup:
                                # import ipdb; ipdb.set_trace()
                                # (values_compare in attvalues_product_bom):
                                # si coinciden todos los ids de los valores
                                # reemplaza el producto original en el BoM Line
                                # por el que encontro
                                # para el caso de una cajonera [2081004NL] tiene
                                # 3 valores de atributos Lado, color cuerpo,
                                # color frente, al pasar a los valores de una
                                # de las lineas del BoM, Frente chico [SP08094904TN]
                                # no va a encontrar el producto a reemplazar por que
                                # no coincide en todos sus valores.
                                # probar segunda parte de la evaluación, en la
                                # que se evalua si el valor de variante del prod
                                # se encuentra en las variantes del producto del BoM
                                if not new_line_product_dup:
                                    new_line.write(
                                        {'product_id': prod.id})

                                # Consulta los factores del (los) valores
                                # de atributo del producto destino (nuevo)
                                # para la linea del BoM
                                self._cr.execute(
                                    """SELECT pav.factor
                                    FROM product_attribute_value_product_product_rel as rel
                                    JOIN product_attribute_value
                                    AS pav ON (pav.id = rel.product_attribute_value_id)
                                    JOIN product_product
                                    AS pp ON (pp.id = rel.product_product_id)
                                    WHERE pp.id = %s AND pav.attribute_id = %s LIMIT 1""",
                                    (prod.id, id_factor))

                                # Si la consulta arrojó al menos un factor:
                                if self._cr.rowcount:
                                    # guarda el primer factor encontrado
                                    # en una variable
                                    factor = self._cr.fetchone()[0]

                                    # Si la cntidad en la nueva línea
                                    # es diferente de cero
                                    if new_line.product_qty != 0:
                                        # Si es que encontró
                                        # algun factor
                                        if factor:
                                            # Si el factor distinto
                                            # de cero
                                            if factor != 0:
                                                # La nueva cantidad
                                                # será igual a
                                                # el factor encontrado
                                                # por el factor a uno
                                                division = \
                                                    cant_factor_uno * factor

                                                # sobreescribe la cantidad calculada
                                                if not new_line_product_dup:
                                                    new_line.with_context(bom_dynamic=True).write(
                                                        {'product_qty': division})
                                                else:
                                                    division += new_line_product_dup.product_qty
                                                    new_line_product_dup.with_context(bom_dynamic=True).write(
                                                        {'product_qty': division})
                                            else:
                                                # Si el factor encontrado
                                                # es igual a cero
                                                # la nueva cantidad
                                                # será a factor uno
                                                if not new_line_product_dup:
                                                    new_line.with_context(bom_dynamic=True).write(
                                                        {'product_qty': cant_factor_uno})
                                                else:
                                                    cant_factor_uno += new_line_product_dup.product_qty
                                                    new_line_product_dup.with_context(bom_dynamic=True).write(
                                                        {'product_qty': cant_factor_uno})
                                        else:
                                            # Si no se encontro ningun factor
                                            # la nueva cantidad es a
                                            # factor uno
                                            if not new_line_product_dup:
                                                new_line.with_context(bom_dynamic=True).write(
                                                    {'product_qty': cant_factor_uno})
                                            else:
                                                cant_factor_uno += new_line_product_dup.product_qty
                                                new_line_product_dup.with_context(bom_dynamic=True).write(
                                                    {'product_qty': cant_factor_uno})
                                    else:
                                        # Si la cantidad original es cero
                                        # regresa error
                                        raise UserError(
                                            _("The quantity in the BoM line can not be zero"))
                                # Copia detalle de corte, con su cuarto detalle (atributos/valores)
                                if new_line_product_dup:
                                    new_line.unlink()
                                    new_line = new_line_product_dup

                                prev_bomline = bml_obj.search(
                                    [('product_id', '=', product_prev_id),
                                     ('bom_id', '=', bom_source.id)], limit=1)
                                mbl_src = prev_bomline[0]
                                for corte in mbl_src.bom_line_detail_ids:
                                    corte_copy = corte.copy({'bom_line_id': new_line.id, 'color_id': False})
                                    corte_copy.write(
                                        {'bom_line_id': new_line.id})
                                    corte_copy.attribute_ids.unlink()
                                    # for value_id in values_compare:
                                    for pvalue in prod.attribute_value_ids:
                                        attribute_obj.create({
                                            'line_detail_id': corte_copy.id,
                                            'attribute_id':
                                                pvalue.attribute_id.id,
                                            'value_ids': [(4, pvalue.id)]
                                        })

                # PROPAGACION POR LINEAS DE REEMPLAZO
                else:
                    # bom_product_id_attvalues = []
                    # global_product_value guarda
                    # todos los productos por reemplazo
                    # de todas las BoM Lines del BoM origen
                    for product_value in global_product_values:
                        # Valida que el producto de la BoM Line
                        # actual no tenga variantes
                        # if not new_line.product_id.product_tmpl_id.reference_mask:
                        # Valida si el producto de la BoM Line actual
                        # es el product de la BoM line del product_value
                        # actual en el loop
                        if new_line.product_id == \
                                product_value.bom_line_value_id.product_id:

                            # Si el producto de reemplazo no aplica para el
                            # Producto del BoM actual, brinca al siguiente
                            if product_value.bom_product_id != \
                                    product_variant_actual:
                                continue

                            # Si conincide el tproducto a reemplazar
                            # y el producto del BoM, reemplazar por el nuevo
                            # producto
                            new_line_product_dup = bml_obj.search([
                                ('product_id', '=', product_value.product_id.id),
                                ('bom_id', '=', bom_new_copy.id),
                                ('id', 'in', new_line_change)],
                                order="id asc", limit=1)

                            if new_line_product_dup:
                                new_cant = new_line_product_dup.product_qty + new_line.product_qty
                                new_line_product_dup.with_context(bom_dynamic=True).write(
                                    {'product_qty': new_cant})
                                new_line.unlink()
                                new_line = new_line_product_dup
                            else:
                                new_line.with_context(bom_dynamic=True).write(
                                    {'product_id': product_value.product_id.id})
                new_line_change.append(new_line.id)
        for bom in new_boms:
            # Revaluar en base al nuevo BoM
            bom.action_reval()
