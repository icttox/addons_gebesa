# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class tms_travel(models.Model):
    _name = 'tms.travel'
    _inherit = ['message.post.show.all', 'tms.travel']

    date_evidence_traf = fields.Datetime(
        string='Fecha Evidencias Trafico',
        copy=False,
    )

    date_evidence_ventas = fields.Datetime(
        string='Fecha Evidencias Ventas',
        copy=False,
    )

    date_evidence_facturacion = fields.Datetime(
        string='Fecha Evidencias Facturación',
        copy=False,
    )

    user_val_trafico_id = fields.Many2one(
        'res.users',
        string='Validado por Trafico:',
        copy=False,
    )

    user_val_ventas_id = fields.Many2one(
        'res.users',
        string='Validado por Ventas:',
        copy=False,
    )

    user_val_fact_id = fields.Many2one(
        'res.users',
        string='Validado por Facturación:',
        copy=False,
    )


    evidencias = fields.Binary(
       string='Evidencias',
       help='Evidencias',
    )

    file_name = fields.Char(
       help='File\'s name')


    @api.multi
    def validation_trafico(self):
        for rec in self:
            user_val_trafico_id = self.env.user
            if not rec.evidencias:
                raise UserError(_('Necesitas adjuntar evidencias en la pestaña de Gestión de Viajes para realizar la validación.'))
            if not self.env.user.has_group('tlm_gebesa.group_manager_validation_trafico'):
                raise UserError(_('No estas asignado para adjuntar evidencias.'))
            rec.user_val_trafico_id = user_val_trafico_id
            rec.date_evidence_traf = fields.Datetime.now()

        return True

    @api.multi
    def validation_ventas(self):
        for rec in self:
            user_val_ventas_id = self.env.user
            if not rec.evidencias:
                raise UserError(_('No se ha adjuntado evidencia.'))
            if not self.env.user.has_group('tlm_gebesa.group_manager_validation_ventas'):
                raise UserError(_('No estas asignado para adjuntar evidencias.'))
            if not rec.date_evidence_traf:
                raise UserError(_('Trafico no ha validado evidencias.'))
            rec.user_val_ventas_id = user_val_ventas_id
            rec.date_evidence_ventas = fields.Datetime.now()

        return True

    @api.multi
    def validation_fact(self):
        for rec in self:
            user_val_fact_id = self.env.user
            if not rec.evidencias:
                raise UserError(_('No se ha adjuntado evidencia.'))
            if not self.env.user.has_group('tlm_gebesa.group_manager_validation_facturacion'):
                raise UserError(_('No estas asignado para adjuntar evidencias.'))
            if not rec.date_evidence_ventas:
                raise UserError(_('Ventas no ha validado evidencias.'))
            rec.user_val_fact_id = user_val_fact_id
            rec.date_evidence_facturacion = fields.Datetime.now()

        return True



#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
