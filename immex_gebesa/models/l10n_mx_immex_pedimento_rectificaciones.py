# -*- coding: utf-8 -*-
# © <2021> <Samuel Barron, GEBESA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class L10nMxImmexPedimentoRectificaciones(models.Model):
    _name = 'l10n.mx.immex.pedimento.rectificaciones'
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
    clave_documento = fields.Char(
        string='Clave del documento',
    )
    fecha_pago = fields.Char(
        string='Fecha de pago',
    )
    num_pedimento_anterior = fields.Char(
        string='Numero de pedimento anterior',
    )
    patente_aduanal_anterior = fields.Char(
        string='Num de patente aduanal anterior',
    )
    clave_aduanal_anterior = fields.Char(
        string='Clave de sección aduanera anterior',
    )
    clave_documento_anterior = fields.Char(
        string='Clave de documento anterior',
    )
    fecha_operacion_anterior = fields.Date(
        string='Fecha de operación anterior',
    )
    num_pedimento_original = fields.Char(
        string='Numero de pedimento original',
    )
    patente_aduanal_original = fields.Char(
        string='Patente aduanal original',
    )
    clave_aduanal_original = fields.Char(
        string='Clave de sección aduanera original',
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
        for ped_rec in self:
            ped_rec.pedimento_id = self.env[
                'l10n.mx.immex.pedimento'].search([
                    ('clave_aduana', '=', ped_rec.clave_aduana),
                    ('num_pedimento', '=', ped_rec.num_pedimento),
                    ('patente', '=', ped_rec.patente)])

    def import_for_data_stage(self, lines, resumen):
        for line in lines:
            line = line.replace('\r\n', '')
            line = line.replace('\x00', '')
            line = line.split("|")

            self.create({
                'patente': line[0],
                'num_pedimento': line[1],
                'clave_aduana': line[2],
                'clave_documento': line[3],
                'fecha_pago': line[4],
                'num_pedimento_anterior': line[5],
                'patente_aduanal_anterior': line[6],
                'clave_aduanal_anterior': line[7],
                'clave_documento_anterior': line[8],
                'fecha_operacion_anterior': line[9],
                'num_pedimento_original': line[10],
                'patente_aduanal_original': line[11],
                'clave_aduanal_original': line[12],
                'fecha_pago_real': line[13],
                'resumen_id': resumen.id,
            })
