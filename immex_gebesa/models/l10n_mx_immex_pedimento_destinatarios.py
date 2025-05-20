# -*- coding: utf-8 -*-
# © <2021> <Samuel Barron, GEBESA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class L10nMxImmexPedimentoDestinatarios(models.Model):
    _name = 'l10n.mx.immex.pedimento.destinatarios'
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
    id_fiscal_destinatario = fields.Char(
        string='Identificación fiscal del destinatario',
    )
    nombre_destinatario = fields.Char(
        string='Nombre del destinatario de la mercancía',
    )
    calle_destinatario = fields.Char(
        string='Calle del domicilio del destinatario',
    )
    num_interior_destinatario = fields.Char(
        string='Numero interior del domicilio del destinatario',
    )
    num_exterior_destinatario = fields.Char(
        string='Numero exterior del domicilio del destinatario',
    )
    cp_destinatario = fields.Char(
        string='Código postal del domicilio del destinatario',
    )
    ciudad_destinatario = fields.Char(
        string='Ciudad del destinatario',
    )
    pais_destinatario = fields.Char(
        string='clave del pais del destinatario',
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
                'id_fiscal_destinatario': line[3],
                'nombre_destinatario': line[4],
                'calle_destinatario': line[5],
                'num_interior_destinatario': line[6],
                'num_exterior_destinatario': line[7],
                'cp_destinatario': line[8],
                'ciudad_destinatario': line[9],
                'pais_destinatario': line[10],
                'fecha_pago_real': line[11],
                'resumen_id': resumen.id,
            })
