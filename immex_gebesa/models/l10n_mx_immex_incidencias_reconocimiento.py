# -*- coding: utf-8 -*-
# © <2021> <Samuel Barron, GEBESA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class L10nMxImmexIncidenciasReconocimiento(models.Model):
    _name = 'l10n.mx.immex.incidencias.reconocimiento'
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
    consecutivo_remesa = fields.Char(
        string='Consecutivo de la remesa',
    )
    numero_seleccion = fields.Char(
        string='Número de selección automatizada',
    )
    fecha_ini = fields.Date(
        string='Fecha de inicio del reconocimiento',
    )
    hora_ini = fields.Char(
        string='Hora de inicio del reconocimiento',
    )
    fecha_fin = fields.Date(
        string='Fecha de fin del reconocimiento',
    )
    hora_fin = fields.Char(
        string='Hora de fin del reconocimiento',
    )
    fraccion_arancelaria = fields.Char(
        string='Fracción arancelaria',
    )
    secuencia_fraccion = fields.Char(
        string='Secuencia de la fracción arancelaria',
    )
    clave_documento = fields.Char(
        string='Clave de documento',
    )
    tipo_operacion = fields.Char(
        string='Clave de tipo de operación',
    )
    grado_incidencia = fields.Char(
        string='Grado de la incidencia',
    )
    fecha_sel_autom = fields.Date(
        string='Fecha de selección automatizada',
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
    partida_id = fields.Many2one(
        'l10n.mx.immex.partida',
        string='Partida',
        compute='_compute_partida_id',
        store=True,
    )

    @api.multi
    @api.depends('clave_aduana', 'num_pedimento', 'patente')
    def _compute_pedimento_id(self):
        for par_per in self:
            par_per.pedimento_id = self.env[
                'l10n.mx.immex.pedimento'].search([
                    ('clave_aduana', '=', par_per.clave_aduana),
                    ('num_pedimento', '=', par_per.num_pedimento),
                    ('patente', '=', par_per.patente)])

    @api.multi
    @api.depends('pedimento_num', 'fraccion_arancelaria', 'secuencia_fraccion')
    def _compute_partida_id(self):
        for inc in self:
            inc.partida_id = self.env[
                'l10n.mx.immex.partida'].search([
                    ('pedimento_num', '=', inc.pedimento_num),
                    ('fraccion_arancelaria', '=', inc.fraccion_arancelaria),
                    ('secuencia_fraccion', '=', inc.secuencia_fraccion)])

    def import_for_data_stage(self, lines, resumen):
        for line in lines:
            line = line.replace('\r\n', '')
            line = line.replace('\x00', '')
            line = line.split("|")

            self.create({
                'patente': line[0],
                'num_pedimento': line[1],
                'clave_aduana': line[2],
                'consecutivo_remesa': line[3],
                'numero_seleccion': line[4],
                'fecha_ini': line[5],
                'hora_ini': line[6],
                'fecha_fin': line[7],
                'hora_fin': line[8],
                'fraccion_arancelaria': line[9],
                'secuencia_fraccion': line[10],
                'clave_documento': line[11],
                'tipo_operacion': line[12],
                'grado_incidencia': line[13],
                'fecha_sel_autom': line[14],
                'resumen_id': resumen.id,
            })
