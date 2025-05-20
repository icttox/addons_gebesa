# -*- coding: utf-8 -*-
# © <2021> <Samuel Barron, GEBESA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class L10nMxImmexPedimentoCuentas(models.Model):
    _name = 'l10n.mx.immex.pedimento.cuentas'
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
    clave_institucion = fields.Char(
        string='Clave de institución emisora',
    )
    numero_cuenta = fields.Char(
        string='Número de cuenta de garantía',
    )
    folio_constancia = fields.Char(
        string='Folio de la constancia de deposito',
    )
    fecha_constancia = fields.Date(
        string='Fecha de la constancia',
    )
    tipo_cuenta = fields.Char(
        string='Clave del tipo de cuenta',
    )
    clave_garantia = fields.Char(
        string='Clave de garantía',
    )
    valor_unitario_titulo = fields.Char(
        string='Valor unitario del título',
    )
    total_garantia = fields.Char(
        string='Total de la garantía',
    )
    cantidad = fields.Char(
        string='Cantidad en unidades de medida del precio estimado',
    )
    titulos = fields.Char(
        string='Titulos asignados',
    )
    fecha_pago_real = fields.Datetime(
        string='Fecha de pago real',
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
        for ped_cue in self:
            ped_cue.pedimento_id = self.env[
                'l10n.mx.immex.pedimento'].search([
                    ('clave_aduana', '=', ped_cue.clave_aduana),
                    ('num_pedimento', '=', ped_cue.num_pedimento),
                    ('patente', '=', ped_cue.patente)])

    def import_for_data_stage(self, lines, resumen):
        for line in lines:
            line = line.replace('\r\n', '')
            line = line.replace('\x00', '')
            line = line.split("|")

            self.create({
                'patente': line[0],
                'num_pedimento': line[1],
                'clave_aduana': line[2],
                'clave_institucion': line[3],
                'numero_cuenta': line[4],
                'folio_constancia': line[5],
                'fecha_constancia': line[6],
                'tipo_cuenta': line[7],
                'clave_garantia': line[8],
                'valor_unitario_titulo': line[9],
                'total_garantia': line[10],
                'cantidad': line[11],
                'titulos': line[12],
                'fecha_pago_real': line[13],
                'resumen_id': resumen.id,
            })
