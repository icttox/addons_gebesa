# -*- coding: utf-8 -*-
# © <2021> <Samuel Barron, GEBESA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class L10nMxImmexPartidaGarantias(models.Model):
    _name = 'l10n.mx.immex.partida.garantias'
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
    clave_emisora = fields.Char(
        string='Clave de institución emisora',
    )
    num_cuenta = fields.Char(
        string='Número de cuenta',
    )
    folio_constancia = fields.Char(
        string='Folio de la constancia',
    )
    fecha_constancia = fields.Date(
        string='Fecha de la constancia',
    )
    clave_garantia = fields.Char(
        string='Clave de la garantía',
    )
    valor_unitario_titulo = fields.Char(
        string='Valor unitario del titulo',
    )
    total_garantia = fields.Char(
        string='Total de la garantía',
    )
    cantidad_udm_estimado = fields.Char(
        string='Cantidad en UdM del precio estimado',
    )
    titulos_asignados = fields.Char(
        string='Titulos asignados',
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
        for par_gar in self:
            par_gar.pedimento_id = self.env[
                'l10n.mx.immex.pedimento'].search([
                    ('clave_aduana', '=', par_gar.clave_aduana),
                    ('num_pedimento', '=', par_gar.num_pedimento),
                    ('patente', '=', par_gar.patente)])

    @api.multi
    @api.depends('pedimento_num', 'fraccion_arancelaria', 'secuencia_fraccion')
    def _compute_partida_id(self):
        for par_gar in self:
            par_gar.partida_id = self.env[
                'l10n.mx.immex.partida'].search([
                    ('pedimento_num', '=', par_gar.pedimento_num),
                    ('fraccion_arancelaria', '=', par_gar.fraccion_arancelaria),
                    ('secuencia_fraccion', '=', par_gar.secuencia_fraccion)])

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
                'clave_emisora': line[5],
                'num_cuenta': line[6],
                'folio_constancia': line[7],
                'fecha_constancia': line[8],
                'clave_garantia': line[9],
                'valor_unitario_titulo': line[10],
                'total_garantia': line[11],
                'cantidad_udm_estimado': line[12],
                'titulos_asignados': line[13],
                'fecha_pago_real': line[14],
                'resumen_id': resumen.id,
            })
