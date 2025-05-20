# -*- coding: utf-8 -*-
# © <2021> <Samuel Barron, GEBESA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class L10nMxImmexPedimentoSeleccion(models.Model):
    _name = 'l10n.mx.immex.pedimento.seleccion'
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
    consecutivo = fields.Char(
        string='Consecutivo de la remesa',
    )
    numero = fields.Char(
        string='Numero de selección automatizada',
    )
    fecha = fields.Date(
        string='Fecha de la selección automatizada',
    )
    hora = fields.Char(
        string='Hora de la selección automatizada',
    )
    semaforo = fields.Char(
        string='Semáforo fiscal',
    )
    clave_documento = fields.Char(
        string='Clave de documento',
    )
    tipo_operacion = fields.Char(
        string='Clave de tipo de operación',
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
        for ped_sel in self:
            ped_sel.pedimento_id = self.env[
                'l10n.mx.immex.pedimento'].search([
                    ('clave_aduana', '=', ped_sel.clave_aduana),
                    ('num_pedimento', '=', ped_sel.num_pedimento),
                    ('patente', '=', ped_sel.patente)])

    def import_for_data_stage(self, lines, resumen):
        for line in lines:
            line = line.replace('\r\n', '')
            line = line.replace('\x00', '')
            line = line.split("|")

            self.create({
                'patente': line[0],
                'num_pedimento': line[1],
                'clave_aduana': line[2],
                'consecutivo': line[3],
                'numero': line[4],
                'fecha': line[5],
                'hora': line[6],
                'semaforo': line[7],
                'clave_documento': line[8],
                'tipo_operacion': line[9],
                'resumen_id': resumen.id,
            })
