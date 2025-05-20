from odoo import fields, models, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')

    zona_salmin = fields.Selection(
        [('A', 'A'),
         ('B', 'B'),
         ('C', 'C')],
        string='Zona Salario Minimo',
        default='A',
    )
    pctjre_integ = fields.Float(
        string='Porcentaje integrado',
    )
    salario_hora = fields.Float(
        string='Salario hora',
        compute='_compute_salario_hora',
        store=True,
    )
    salario_integ = fields.Float(
        string='Salario Integrado',
    )
    dto_infonavit_mensual = fields.Float(
        string='Descuento infonavit mensual',
    )
    dto_infonavit_diario = fields.Float(
        string='Descuento infonavit diario',
        compute='_compute_dto_infonavit_diario',
    )
    dto_fonacot_mensual = fields.Float(
        string='Descuento fonacot mensual',
    )
    dto_fonacot_semanal = fields.Float(
        string='Descuento fonacot semanal',
        compute='_compute_dto_fonacot_semanal',
    )
    ptu = fields.Boolean(
        string='PTU',
    )
    imss = fields.Boolean(
        string='IMSS',
    )
    cas = fields.Boolean(
        string='CAS',
    )
    pensionado = fields.Boolean(
        string='Pensionado',
    )
    deshab_imptos = fields.Boolean(
        string='Deshab imptos',
    )
    calc_isr_anual = fields.Boolean(
        string='Calculo ISR anual',
    )
    periodicidad_pago = fields.Selection(
        selection=[
            ('01', 'Diario'),
            ('02', 'Semanal'),
            ('03', 'Catorcenal'),
            ('04', 'Quincenal'),
            ('05', 'Mensual'),
            ('06', 'Bimensual'),
            ('07', 'Unidad obra'),
            ('08', 'Comisión'),
            ('09', 'Precio alzado'),
            ('10', 'Pago por consignación'),
            ('99', 'Otra periodicidad')],
        string='Periodicidad de pago CFDI',
    )
    riesgo_puesto = fields.Selection(
        selection=[
            ('1', 'Clase I'),
            ('2', 'Clase II'),
            ('3', 'Clase III'),
            ('4', 'Clase IV'),
            ('5', 'Clase V'),
            ('99', 'No aplica')],
        string='Riesgo del puesto',
    )
    regimen = fields.Selection(
        selection=[
            ('02', '02 - Sueldos'),
            ('03', '03 - Jubilados'),
            ('04', '04 - Pensionados'),
            ('05', '05 - Asimilados Miembros Sociedades Cooperativas Produccion'),
            ('06', '06 - Asimilados Integrantes Sociedades Asociaciones Civiles'),
            ('07', '07 - Asimilados Miembros consejos'),
            ('08', '08 - Asimilados comisionistas'),
            ('09', '09 - Asimilados Honorarios'),
            ('10', '10 - Asimilados acciones'),
            ('11', '11 - Asimilados otros'),
            ('12', '12 - Jubilados o Pensionados'),
            ('13', '13 - Indemnización o Separación'),
            ('99', '99 - Otro Regimen')],
        string='Régimen',
    )
    contrato = fields.Selection(
        selection=[
            ('01', '01 - Contrato de trabajo por tiempo indeterminado'),
            ('02', '02 - Contrato de trabajo para obra determinada'),
            ('03', '03 - Contrato de trabajo por tiempo determinado'),
            ('04', '04 - Contrato de trabajo por temporada'),
            ('05', '05 - Contrato de trabajo sujeto a prueba'),
            ('06', '06 - Contrato de trabajo con capacitación inicial'),
            ('07', '07 - Modalidad de contratación por pago de hora laborada'),
            ('08', '08 - Modalidad de trabajo por comisión laboral'),
            ('09', '09 - Modalidades de contratación donde no existe relación de trabajo'),
            ('10', '10 - Jubilación, pensión, retiro'),
            ('99', '99 - Otro contrato')],
        string='Contrato',
    )
    jornada = fields.Selection(
        selection=[
            ('01', '01 - Diurna'),
            ('02', '02 - Nocturna'),
            ('03', '03 - Mixta'),
            ('04', '04 - Por hora'),
            ('05', '05 - Reducida'),
            ('06', '06 - Continuada'),
            ('07', '07 - Partida'),
            ('08', '08 - Por turnos'),
            ('99', '99 - Otra Jornada')],
        string='Jornada',
    )

    @api.depends('salario_diario')
    def _compute_salario_hora(self):
        for rec in self:
            rec.salario_hora = (rec.salario_diario / 8)

    @api.depends('dto_infonavit_mensual')
    def _compute_dto_infonavit_diario(self):
        for rec in self:
            rec.dto_infonavit_diario = (rec.dto_infonavit_mensual * 2) / 60.8

    @api.depends('dto_fonacot_mensual')
    def _compute_dto_fonacot_semanal(self):
        for rec in self:
            rec.dto_fonacot_semanal = rec.dto_fonacot_mensual / 4

    # @api.onchange('salario_diario')
    # def onchange_wage(self):
    #     for rec in self:
    #         rec.wage = rec.salario_diario * 30.4166

    # wage = fields.Monetary(
        # compute='_compute_wage',
        # store=True,
    # )

    # @api.depends('salario_diario')
    # def _compute_wage(self):
        # for rec in self:
            # rec.wage = rec.salario_diario * 30.4166
