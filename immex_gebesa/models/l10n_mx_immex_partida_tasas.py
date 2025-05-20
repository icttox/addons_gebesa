# -*- coding: utf-8 -*-
# © <2021> <Samuel Barron, GEBESA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class L10nMxImmexPartidaTasas(models.Model):
    _name = 'l10n.mx.immex.partida.tasas'
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
    fraccion_arancelaria = fields.Char(
        string='Fracción arancelaria',
    )
    secuencia_fraccion = fields.Char(
        string='Secuencia de la fracción arancelaria',
    )
    clave_contribucion = fields.Char(
        string='Clave de la contribución',
    )
    tasa_contribucion = fields.Char(
        string='Tasa de la contribución',
    )
    tipo_tasa = fields.Char(
        string='Clave de tipo de la tasa',
    )
    fecha_pago_real = fields.Datetime(
        string='Fecha de pago de las contribuciones y cuotas',
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
    clave_documento = fields.Char(
        string='Clave del documento',
        related='pedimento_id.clave_documento',
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
        for par_tas in self:
            par_tas.pedimento_id = self.env[
                'l10n.mx.immex.pedimento'].search([
                    ('clave_aduana', '=', par_tas.clave_aduana),
                    ('num_pedimento', '=', par_tas.num_pedimento),
                    ('patente', '=', par_tas.patente)])

    @api.multi
    @api.depends('pedimento_num', 'fraccion_arancelaria', 'secuencia_fraccion')
    def _compute_partida_id(self):
        for par_tas in self:
            par_tas.partida_id = self.env[
                'l10n.mx.immex.partida'].search([
                    ('pedimento_num', '=', par_tas.pedimento_num),
                    ('fraccion_arancelaria', '=', par_tas.fraccion_arancelaria),
                    ('secuencia_fraccion', '=', par_tas.secuencia_fraccion)])

    def import_for_data_stage(self, lines, resumen):
        for line in lines:
            line = line.replace('\r\n', '')
            line = line.replace('\x00', '')
            line = line.split("|")

            self.create({
                'patente': line[0],
                'num_pedimento': line[1],
                'clave_aduana': line[2],
                'fraccion_arancelaria': line[3],
                'secuencia_fraccion': line[4],
                'clave_contribucion': line[5],
                'tasa_contribucion': line[6],
                'tipo_tasa': line[7],
                'fecha_pago_real': line[8],
                'resumen_id': resumen.id,
            })
