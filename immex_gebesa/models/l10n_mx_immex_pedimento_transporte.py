# -*- coding: utf-8 -*-
# © <2021> <Samuel Barron, GEBESA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class L10nMxImmexPedimentoTransporte(models.Model):
    _name = 'l10n.mx.immex.pedimento.transporte'
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
    rfc_transportirsta = fields.Char(
        string='RFC del transportista',
    )
    curp_transportista = fields.Char(
        string='CURP del transportista',
    )
    nombre_transportista = fields.Char(
        string='Razón social del transportista',
    )
    pais_transportista = fields.Char(
        string='Clave del país del transportista',
    )
    id_transporte = fields.Char(
        string='Identificación del transporte que introduce las mercancías',
    )
    fecha_pago_transport = fields.Datetime(
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
        for ped_tra in self:
            ped_tra.pedimento_id = self.env[
                'l10n.mx.immex.pedimento'].search([
                    ('clave_aduana', '=', ped_tra.clave_aduana),
                    ('num_pedimento', '=', ped_tra.num_pedimento),
                    ('patente', '=', ped_tra.patente)])

    def import_for_data_stage(self, lines, resumen):
        for line in lines:
            line = line.replace('\r\n', '')
            line = line.replace('\x00', '')
            line = line.split("|")

            self.create({
                'patente': line[0],
                'num_pedimento': line[1],
                'clave_aduana': line[2],
                'rfc_transportirsta': line[3],
                'curp_transportista': line[4],
                'nombre_transportista': line[5],
                'pais_transportista': line[6],
                'id_transporte': line[7],
                'fecha_pago_transport': line[8],
                'resumen_id': resumen.id,
            })
