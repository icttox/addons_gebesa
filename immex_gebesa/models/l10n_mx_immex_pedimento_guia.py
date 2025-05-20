# -*- coding: utf-8 -*-
# © <2021> <Samuel Barron, GEBESA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class L10nMxImmexPedimentoGuia(models.Model):
    _name = 'l10n.mx.immex.pedimento.guia'
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
    numero_guia = fields.Char(
        string='Numeros de guia o manifiesto',
    )
    tipo_guia = fields.Char(
        string='Tipo de Guía',
    )
    fecha_pago_guia = fields.Datetime(
        string='Fecha de pago real de las contribuciones',
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
        for ped_gui in self:
            ped_gui.pedimento_id = self.env[
                'l10n.mx.immex.pedimento'].search([
                    ('clave_aduana', '=', ped_gui.clave_aduana),
                    ('num_pedimento', '=', ped_gui.num_pedimento),
                    ('patente', '=', ped_gui.patente)])

    def import_for_data_stage(self, lines, resumen):
        for line in lines:
            line = line.replace('\r\n', '')
            line = line.replace('\x00', '')
            line = line.split("|")

            self.create({
                'patente': line[0],
                'num_pedimento': line[1],
                'clave_aduana': line[2],
                'numero_guia': line[3],
                'tipo_guia': line[4],
                'fecha_pago_guia': line[5],
                'resumen_id': resumen.id,
            })
