# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BomSelectiveReplace(models.Model):
    _name = 'bom.selective.replace'
    _description = 'Bom Selective Replace'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Code',
        size=64,
    )

    date = fields.Date(
        string='Date',
        default=fields.Date.today,
    )

    state = fields.Selection(
        [('draft', 'Draft'),
        ('done', 'Done')],
        string='State',
        default='draft',
    )

    lines_ids = fields.One2many(
        'bom.selective.replace.line',
        'bom_selective_id',
        string='Bom Massive lines',
    )

    @api.multi
    def get_selective_sql(self):
        insert_lines = []
        for line in self.lines_ids:

            # Busca producto encabezado del BoM original -OK
            self._cr.execute(
                """SELECT id
                FROM product_product
                WHERE default_code = %s
                AND active = True""", ([line.original]))
            # Si no existe registra mensaje de error
            if self._cr.rowcount:
                resultado = self._cr.fetchall()
                id_encab = resultado[0]
            else:
                raise UserError(_(
                    'The original BoM Product does not exists %s, verify please...') % line.original)

            # Busca producto de la linea del BoM original -OK
            self._cr.execute(
                """SELECT id
                FROM product_product
                WHERE default_code = %s
                AND active = True""", ([line.code_current]))
            # Si no existe registra mensaje de error
            if self._cr.rowcount:
                resultado = self._cr.fetchall()
                id_linea = resultado[0]
            else:
                raise UserError(_(
                    'The original BoM line Product does not exists %s, verify please...') % line.code_current)

            # Busca producto del Encabezado del BoM destino
            self._cr.execute(
                """SELECT id
                FROM product_product
                WHERE default_code = %s
                AND active = True""", ([line.code_master]))
            # Si no existe registra mensaje de error
            if self._cr.rowcount:
                resultado = self._cr.fetchall()
                id_encabdest = resultado[0]
            else:
                raise UserError(_(
                    'The target BoM Product does not exists %s, verify please...') % line.code_master)

            # Busca producto de la Linea del BoM destino
            self._cr.execute(
                """SELECT id
                FROM product_product
                WHERE default_code = %s
                AND active = True""", ([line.code_update]))
            # Si no existe registra mensaje de error
            if self._cr.rowcount:
                resultado = self._cr.fetchall()
                id_lineadest = resultado[0]
            else:
                raise UserError(_(
                    'The target BoM line Product does not exists %s, verify please...') % line.code_update)

            # Busca el BoM original
            self._cr.execute(
                """SELECT id
                FROM mrp_bom WHERE product_id = %s
                AND active = True""", ([id_encab]))
            # Si no existe registra mensaje de error
            if self._cr.rowcount:
                resultado = self._cr.fetchall()
                id_bom = resultado[0]
            else:
                raise UserError(_(
                    'The original Bill of materials does not exists %s, verify please...') % line.original)

            # Busca el Bom Line original
            self._cr.execute(
                """SELECT id
                FROM mrp_bom_line
                WHERE bom_id = %s
                AND product_id = %s""", (id_bom, id_linea))
            if self._cr.rowcount:
                bom_line = self._cr.fetchone()
                id_bomline = bom_line[0]
            else:
                raise UserError(_(
                    'The original BoM line does not exists %s, verify please...') % line.code_current)

            insert_lines.append({
                'id_bomline': id_bomline,
                'id_encabdest': id_encabdest,
                'id_lineadest': id_lineadest})

        for line in insert_lines:
            if line['id_bomline'] and line['id_encabdest'] and line['id_lineadest']:
                self._cr.execute("""
                    INSERT INTO mrp_bom_product_replacement(
                    create_uid,create_date,product_id,bom_line_value_id,
                    write_uid,write_date,bom_product_id)
                        VALUES(1,NOW(),%s,%s,1,NOW(),%s)""",
                                 (line['id_lineadest'], line['id_bomline'], line['id_encabdest']))
        self.state = 'done'


class BomSelectiveReplaceLine(models.Model):
    _name = 'bom.selective.replace.line'
    _description = 'Bom Selective Replace Line'

    bom_selective_id = fields.Many2one(
        'bom.selective.replace',
        string='Bom Selective Replace',
        ondelete='cascade',
        index=2,
        required=True,
    ) # Id de la linea de detalle donde se congarán todos los productos de reemplazo
    # Se busca con el original y el code_master

    original = fields.Char(
        string='Original',
        required=True,
    ) # Producto original del encabezado del BoM

    code_master = fields.Char(
        string='Header Key',
        required=True,
    ) # Producto de la linea de detale (BoM Line) Original

    code_current = fields.Char(
        string='Original Detail',
    ) # Producto destino del encabezado del BoM

    code_update = fields.Char(
        string='Update Code',
        required=True,
    ) # Producto de reemplazo en la linea de detalle (BoM Line) Destino
