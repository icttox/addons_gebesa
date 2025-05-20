# -*- coding: utf-8 -*-
# © <2021> <Samuel Barron, GEBESA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class L10nMxImmexPedimentoTasas(models.Model):
    _name = 'l10n.mx.immex.pedimento.tasas'
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
    clave_contribucion = fields.Char(
        string='Clave de contribución',
    )
    tasa = fields.Char(
        string='Tasa de contribución',
    )
    tipo_tasa = fields.Char(
        string='Clave de tipo de tasa',
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
    clave_documento = fields.Char(
        string='Clave del documento',
        related='pedimento_id.clave_documento',
        store=True,
    )

    @api.multi
    @api.depends('clave_aduana', 'num_pedimento', 'patente')
    def _compute_pedimento_id(self):
        for ped_tas in self:
            ped_tas.pedimento_id = self.env[
                'l10n.mx.immex.pedimento'].search([
                    ('clave_aduana', '=', ped_tas.clave_aduana),
                    ('num_pedimento', '=', ped_tas.num_pedimento),
                    ('patente', '=', ped_tas.patente)])

    def import_for_data_stage(self, lines, resumen):
        for line in lines:
            line = line.replace('\r\n', '')
            line = line.replace('\x00', '')
            line = line.split("|")

            self.create({
                'patente': line[0],
                'num_pedimento': line[1],
                'clave_aduana': line[2],
                'clave_contribucion': line[3],
                'tasa': line[4],
                'tipo_tasa': line[5],
                'tipo_pedimento': line[6],
                'fecha_pago_real': line[7],
                'resumen_id': resumen.id,
            })
