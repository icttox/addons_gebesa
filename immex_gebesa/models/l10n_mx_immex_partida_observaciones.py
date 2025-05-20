# -*- coding: utf-8 -*-
# © <2021> <Samuel Barron, GEBESA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class L10nMxImmexPartidaObservaciones(models.Model):
    _name = 'l10n.mx.immex.partida.observaciones'
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
    secuencia_observacion = fields.Char(
        string='Secuencia de observaciones',
    )
    observaciones = fields.Char(
        string='observaciones',
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
        for par_obs in self:
            par_obs.pedimento_id = self.env[
                'l10n.mx.immex.pedimento'].search([
                    ('clave_aduana', '=', par_obs.clave_aduana),
                    ('num_pedimento', '=', par_obs.num_pedimento),
                    ('patente', '=', par_obs.patente)])

    @api.multi
    @api.depends('pedimento_num', 'fraccion_arancelaria', 'secuencia_fraccion')
    def _compute_partida_id(self):
        for par_obs in self:
            par_obs.partida_id = self.env[
                'l10n.mx.immex.partida'].search([
                    ('pedimento_num', '=', par_obs.pedimento_num),
                    ('fraccion_arancelaria', '=', par_obs.fraccion_arancelaria),
                    ('secuencia_fraccion', '=', par_obs.secuencia_fraccion)])

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
                'secuencia_observacion': line[5],
                'observaciones': line[6],
                'fecha_pago_real': line[7],
                'resumen_id': resumen.id,
            })
