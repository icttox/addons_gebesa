# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    time_type = fields.Selection(
        string='Tipo de ausencia',
        related='holiday_status_id.time_type',)
    ramo_seguro = fields.Selection(
        [('R', 'Riesgo de trabajo'),
         ('E', 'Enfermedad'),
         ('M', 'Maternidad')],
        string='Ramo de seguro',
        default='R',
    )
    tipo_riesgo = fields.Selection(
        [('1', 'Accidente de trabajo'),
         ('2', 'Accidente en trayecto'),
         ('3', 'Enfermedad de trabajo')],
        string='Tipo de riesgo',
    )
    secuela = fields.Selection(
        [('0', 'Ninguna'),
         ('1', 'Incapacidad temporal'),
         ('2', 'Valuacion inicial provisional'),
         ('3', 'Valuacion inicial definitiva'),
         ('4', 'Defucion'),
         ('5', 'Recaida'),
         ('6', 'Valuacion post. a la fecha de alta'),
         ('7', 'Revaluacion provisional'),
         ('8', 'Recaida sin alta medica'),
         ('9', 'Revaluacion definitiva')],
        string='Secuela',
    )
    incapacidad_folio = fields.Char(
        string='Folio',
    )
    control = fields.Selection(
        [('0', 'Ninguna'),
         ('1', 'Unica'),
         ('2', 'Inicial'),
         ('3', 'Subsecuente'),
         ('4', 'Alta medica o ST-2'),
         ('5', 'Valuacion o ST-3'),
         ('6', 'Defuncion o ST-3'),
         ('7', 'Prenatal o ST-3'),
         ('8', 'Enlace'),
         ('9', 'Postnatal')],
        string='Control',
    )
    porcentaje = fields.Float(
        string='Porcentaje',
    )

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        if employee_id and not self.holiday_status_id.working_days:
            calendar = self.env.ref('gebesa_integracion_microsip.calendar_inhability_leave', False)
            if calendar:
                employee = self.env['hr.employee'].browse(employee_id)
                return employee.get_work_days_data(date_from, date_to, calendar=calendar)['days']

        return super()._get_number_of_days(date_from, date_to, employee_id)
