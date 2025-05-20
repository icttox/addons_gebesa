# -*- coding: utf-8 -*-
# © <2021> <Samuel Barron, GEBESA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class L10nMxImmexPedimentoDescargos(models.Model):
    _name = 'l10n.mx.immex.pedimento.descargos'
    _rec_name = 'pedimento_num'
    _description = 'descripcion pendiente'

    patente = fields.Char(
        string='patente',
    )
    num_pedimento = fields.Char(
        string='Numero pedimento',
    )
    clave_aduana = fields.Char(
        string='Clave aduana',
    )
    patente_original = fields.Char(
        string='Patente aduana original',
    )
    numero_original = fields.Char(
        string='Número de pedimento original',
    )
    clave_seccion_original = fields.Char(
        string='Clave de sección aduanera original',
    )
    clave_documento_original = fields.Char(
        string='Clave de pedimento de que se trate',
    )
    fecha_operacion_original = fields.Date(
        string='Fecha operacion original',
    )
    fraccion_areancelaria_original = fields.Char(
        string='Fracción arancelaria original',
    )
    udm_original = fields.Char(
        string='Clave de unidad de medida original',
    )
    cantidad = fields.Char(
        string='Cantidad de mercancía descargada',
    )
    tipo_pedimento = fields.Char(
        string='Clave de tipo de pedimento',
    )
    fecha_pago_real = fields.Datetime(
        string='Fecha pago real',
    )
    resumen_id = fields.Many2one(
        'l10n.mx.immex.resumen',
        string='Resumen id',
    )
    pedimento_id = fields.Many2one(
        'l10n.mx.immex.pedimento',
        string='Pedimento',
        compute='_compute_pedimento_id',
        store=True,
    )
    pedimento_num = fields.Char(
        string='Pedimento Numero',
        related='pedimento_id.pedimento_num',
        store=True,
    )

    @api.multi
    @api.depends('clave_aduana', 'num_pedimento', 'patente')
    def _compute_pedimento_id(self):
        for ped_des in self:
            ped_des.pedimento_id = self.env[
                'l10n.mx.immex.pedimento'].search([
                    ('clave_aduana', '=', ped_des.clave_aduana),
                    ('num_pedimento', '=', ped_des.num_pedimento),
                    ('patente', '=', ped_des.patente)])

    def import_for_data_stage(self, lines, resumen):
        for line in lines:
            line = line.replace('\r\n', '')
            line = line.replace('\x00', '')
            line = line.split("|")

            self.create({
                'patente': line[0],
                'num_pedimento': line[1],
                'clave_aduana': line[2],
                'patente_original': line[3],
                'numero_original': line[4],
                'clave_seccion_original': line[5],
                'clave_documento_original': line[6],
                'fecha_operacion_original': line[7],
                'fraccion_areancelaria_original': line[8],
                'udm_original': line[9],
                'cantidad': line[10],
                'tipo_pedimento': line[11],
                'fecha_pago_real': line[12],
                'resumen_id': resumen.id,
            })
