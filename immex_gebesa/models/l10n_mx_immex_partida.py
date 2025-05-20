# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, api, models
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp


class L10nMxImmexPartida(models.Model):
    _name = 'l10n.mx.immex.partida'
    _inherit = ['message.post.show.all']
    _rec_name = 'pedimento_num'

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
    subdivision_fraccion = fields.Char(
        string='Subdivisión de la fracción arancelaria',
    )
    descripcion = fields.Char(
        string='Descripción de la mercancía',
    )
    precio_unitario = fields.Char(
        string='Precio Unitario',
    )
    valor_aduana = fields.Char(
        string='Valor en aduana',
    )
    valor_comercial = fields.Char(
        string='Valor comercial',
    )
    valor_usd = fields.Char(
        string='Valor en dólares',
    )
    cantidad_udm_comercial = fields.Char(
        string='Cantidad en udm comercial',
    )
    udm_comercial = fields.Char(
        string='Clave de unidad de medida comercial',
    )
    cantidad_udm_tarifa = fields.Char(
        string='Cantidad correspondiente a udm TIGIE',
    )
    udm_tarifa = fields.Char(
        string='Clave de unidad de medida de la tarifa',
    )
    valor_agregado = fields.Char(
        string='Valor agregado',
    )
    clave_vinculacion = fields.Char(
        string='Clave de vinculación',
    )
    metodo_valorizacion = fields.Char(
        string='Clave del método de valorización',
    )
    codigo_mercancia = fields.Char(
        string='Código de la mercancía o producto',
    )
    marca_mercancia = fields.Char(
        string='Marca de la mercancía o producto',
    )
    modelo_mercancia = fields.Char(
        string='Modelo de la mercancía o producto',
    )
    pais = fields.Char(
        string='Clave de país Origen/Destino',
    )
    pais_extranjero = fields.Char(
        string='Clave de país Comprador/Vendedor',
    )
    estado_origen = fields.Char(
        string='Clave de entidad federativa de origen',
    )
    estado_destino = fields.Char(
        string='Clave de entidad federativa de destino',
    )
    estado_comprador = fields.Char(
        string='Clave de entidad federativa del comprador',
    )
    estado_vendedor = fields.Char(
        string='Clave de entidad federativa del vendedor',
    )
    tipo_operacion = fields.Char(
        string='Clave de tipo de operación',
    )
    clave_documento = fields.Char(
        string='Clave de documento',
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
    amount = fields.Float(
        string='Saldo',
    )
    immex_type_id = fields.Many2one(
        'l10n.mx.immex.partida.type',
        required=False,
        string='Immex Clasificación',
    )
    porcentaje_desperdicio = fields.Float(
        string='% Desperdicio',
        digits=dp.get_precision('Account')
    )
    materials_code = fields.Text(
        string='Clave de materiales',
        compute='_get_materials_code',
    )
    regime_changed = fields.Boolean(
        string='Cambio de Régimen',
    )
    saldo_mxn_pendiente = fields.Float(
        string='Saldo en pesos pendiente',
        compute='_get_saldo_mxn_pendiente',
    )
    permisos_ids = fields.One2many(
        'l10n.mx.immex.partida.permisos',
        'partida_id',
        string='Permisos'
    )
    garantias_ids = fields.One2many(
        'l10n.mx.immex.partida.garantias',
        'partida_id',
        string='Garantias'
    )
    tasas_ids = fields.One2many(
        'l10n.mx.immex.partida.tasas',
        'partida_id',
        string='Tasas'
    )
    contribuciones_ids = fields.One2many(
        'l10n.mx.immex.partida.contribuciones',
        'partida_id',
        string='Contribuciones'
    )
    incidencias_ids = fields.One2many(
        'l10n.mx.immex.incidencias.reconocimiento',
        'partida_id',
        string='Incidencias'
    )
    mercancias_ids = fields.One2many(
        'l10n.mx.immex.mercancias',
        'partida_id',
        string='Mercancias'
    )
    casos_ids = fields.One2many(
        'l10n.mx.immex.partida.casos',
        'partida_id',
        string='Casos'
    )
    descargue_line_ids = fields.One2many(
        'l10n.mx.immex.partida.descargue.line',
        'partida_id',
        string='Descargue Linea'
    )

    regularization_entry_id = fields.Many2one(
        'l10n.mx.immex.partida',
        string='Partida de regularización',
    )

    cantidad_udm_comercial_related = fields.Char(
        string='Cantidad regularizada',
        related='regularization_entry_id.cantidad_udm_comercial',
    )

    @api.multi
    @api.depends('secuencia_fraccion', 'fraccion_arancelaria', 'descripcion')
    def name_get(self):
        res = []
        for partida in self:
            res.append((partida.id, "%s - %s - %s" % (
                (partida.secuencia_fraccion or ''),
                (partida.fraccion_arancelaria or ''),
                (partida.descripcion or ''))))
        return res

    @api.constrains('porcentaje_desperdicio')
    def _ckeck_porcentaje(self):
        if (self.porcentaje_desperdicio > 100) or (self.porcentaje_desperdicio < 0.00):
            raise ValidationError(_('The percentage must be strictly positive but less than 100.'))

    @api.multi
    @api.depends('clave_aduana', 'num_pedimento', 'patente')
    def _compute_pedimento_id(self):
        for par_per in self:
            par_per.pedimento_id = self.env[
                'l10n.mx.immex.pedimento'].search([
                    ('clave_aduana', '=', par_per.clave_aduana),
                    ('num_pedimento', '=', par_per.num_pedimento),
                    ('patente', '=', par_per.patente)])

    @api.depends('immex_type_id')
    def _get_materials_code(self):
        for partida in self:
            materials_code = ''
            if partida.immex_type_id:
                product_ids = self.env['product.product'].search([
                    ('immex_type_id', '=', partida.immex_type_id.id),
                    ('default_code', '!=', False)])
                if product_ids:
                    materials_code = ', '.join(product_ids.mapped(
                        'default_code'))
            partida.materials_code = materials_code

    @api.depends('amount', 'precio_unitario')
    def _get_saldo_mxn_pendiente(self):
        for partida in self:
            partida.saldo_mxn_pendiente = round(
                partida.amount * float(partida.precio_unitario), 2)

    @api.multi
    def print_initial_inventory(self):
        partidas = self.search([
            ('amount', '>', 0.00),
            ('clave_documento', 'in', ['IN', 'V1', 'AF'])]).ids
        return self.env.ref(
            'immex_gebesa.immex_initial_inventory').report_action(partidas)

    def import_for_data_stage(self, lines, resumen):
        for line in lines:
            line = line.replace('\r\n', '')
            line = line.replace('\x00', '')
            line = line.split("|")

            partida = self.search([
                ('patente', '=', line[0]),
                ('num_pedimento', '=', line[1]),
                ('clave_aduana', '=', line[2]),
                ('fraccion_arancelaria', '=', line[3]),
                ('secuencia_fraccion', '=', line[4])])
            if partida:
                partida.write({
                    'subdivision_fraccion': line[5],
                    'descripcion': line[6],
                    'precio_unitario': line[7],
                    'valor_aduana': line[8],
                    'valor_comercial': line[9],
                    'valor_usd': line[10],
                    'cantidad_udm_comercial': line[11],
                    'udm_comercial': line[12],
                    'cantidad_udm_tarifa': line[13],
                    'udm_tarifa': line[14],
                    'valor_agregado': line[15],
                    'clave_vinculacion': line[16],
                    'metodo_valorizacion': line[17],
                    'codigo_mercancia': line[18],
                    'marca_mercancia': line[19],
                    'modelo_mercancia': line[20],
                    'pais': line[21],
                    'pais_extranjero': line[22],
                    'estado_origen': line[23],
                    'estado_destino': line[24],
                    'estado_comprador': line[25],
                    'estado_vendedor': line[26],
                    'tipo_operacion': line[27],
                    'clave_documento': line[28],
                    'fecha_pago_real': line[29],
                    'resumen_id': resumen.id,
                })
            else:
                amount = 0
                if line[28] == 'IN':
                    amount = line[11]
                self.create({
                    'patente': line[0],
                    'num_pedimento': line[1],
                    'clave_aduana': line[2],
                    'fraccion_arancelaria': line[3],
                    'secuencia_fraccion': line[4],
                    'subdivision_fraccion': line[5],
                    'descripcion': line[6],
                    'precio_unitario': line[7],
                    'valor_aduana': line[8],
                    'valor_comercial': line[9],
                    'valor_usd': line[10],
                    'cantidad_udm_comercial': line[11],
                    'udm_comercial': line[12],
                    'cantidad_udm_tarifa': line[13],
                    'udm_tarifa': line[14],
                    'valor_agregado': line[15],
                    'clave_vinculacion': line[16],
                    'metodo_valorizacion': line[17],
                    'codigo_mercancia': line[18],
                    'marca_mercancia': line[19],
                    'modelo_mercancia': line[20],
                    'pais': line[21],
                    'pais_extranjero': line[22],
                    'estado_origen': line[23],
                    'estado_destino': line[24],
                    'estado_comprador': line[25],
                    'estado_vendedor': line[26],
                    'tipo_operacion': line[27],
                    'clave_documento': line[28],
                    'fecha_pago_real': line[29],
                    'resumen_id': resumen.id,
                    'amount': amount
                })
