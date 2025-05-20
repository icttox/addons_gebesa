# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError
from werkzeug.urls import url_encode


_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    product_id = fields.Many2one(
        'product.template',
        string='Product',
        index=True,
        track_visibility='always'
    )

    order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        index=True,
        track_visibility='always'
    )

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        index=True,
        track_visibility='always')

    muestra = fields.Boolean(
        string='Sample',
    )

    clave = fields.Boolean(
        string='Key',
    )

    costo = fields.Boolean(
        string='Cost',
    )

    planted = fields.Boolean(
        string='Planted',
    )

    render = fields.Boolean(
        string='Render',
    )

    planos = fields.Boolean(
        string='Planes',
    )

    user_val_id = fields.Many2one(
        'res.users',
        string='Validado por IP:',
        copy=False,
    )

    user_val_aip_id = fields.Many2one(
        'res.users',
        string='Validado por AIP:',
        copy=False,
    )

    user_val_diseno_id = fields.Many2one(
        'res.users',
        string='Validado por Diseño:',
        copy=False,
    )

    validation_time_ip = fields.Datetime(
        string='Fecha de Validación IP',
        copy=False,
    )

    validation_time_aip = fields.Datetime(
        string='Fecha de Validación AIP',
        copy=False,
    )

    validation_time_diseno = fields.Datetime(
        string=u'Fecha de Validación Diseño',
        copy=False,
    )

    validation_ip = fields.Selection(
        [('approved', 'Aprobado'),
         ('not_approved', 'No Aprobado')],
        default='not_approved',
        string='Estatus de Validación IP',
        store=True,
        copy=False,
    )

    validation_aip = fields.Selection(
        [('approved', 'Aprobado'),
         ('not_approved', 'No Aprobado')],
        default='not_approved',
        string='Estatus de Validación AIP',
        store=True,
        copy=False,
    )

    validation_diseno = fields.Selection(
        [('approved', 'Aprobado'),
         ('not_approved', 'No Aprobado')],
        default='not_approved',
        string='Estatus de Validación Diseño',
        store=True,
        copy=False,
    )
    # archive = fields.Binary(
    #     string=_("Archivo del Checklist"),
    #     attachment=True,
    #     copy=False,
    # )

    special_a = fields.Boolean(
        string='ESPECIFICAR QUE ES ESPECIAL Y POR QUE',
        copy=False,
    )

    special_b = fields.Boolean(
        string='ACLARAR CORRECTAMENTE SI ES SEMI-ESPECIAL O ESPECIAL',
        copy=False,
    )

    special_c = fields.Boolean(
        string='CHECAR QUE EL CAMBIO EN EL PRECIO ESTE APLICADO',
        copy=False,
    )

    special_d = fields.Boolean(
        string='SUBRAYAR EN AMARILLO LO QUE ES ESPECIAL',
        copy=False,
    )

    special_e = fields.Boolean(
        string='ESPECIFICAR LA JALADERA QUE SE UTILIZARA Y CHECAR EL COLOR',
        copy=False,
    )

    special_f = fields.Boolean(
        string='SI EL PASACABLE / RESAQUE VA EN UNA POSICION ESPECIAL, INCLUIR PLANO',
        copy=False,
    )

    special_g = fields.Boolean(
        string='SI NOS PIDEN MEDIDAS ESPECIALES EN CUBIERTAS, VERIFICAR QUE SE INCLUYAN LOS HERRAJES NECESARIOS',
        copy=False,
    )

    general_a = fields.Boolean(
        string='INCLUIR CLAVE Y DESCRIPCION COMPLETA CON ACABADOS',
        copy=False,
    )

    general_b = fields.Boolean(
        string='VERIFICAR LA POSICION Y EL COLOR DE LOS PASACABLES CON EL CLIENTE Y CHECAR SI ES DE LINEA O SEMI ESPECIAL',
        copy=False,
    )

    general_c = fields.Boolean(
        string='REVISAR QUE EL RENDER COINCIDA CON LO SOLICITADO (MUEBLES Y ACABADOS)',
        copy=False,
    )

    general_d = fields.Boolean(
        string='ESPECIFICAR MEDIDAS DE LAS PERFORACIONES EN LAS CUBIERTAS DEPENDIENDO DEL MULTICONTACTO (CHECAR QUE SE INCLUYA PLANO DE BYRNE)',
        copy=False,
    )

    general_e = fields.Boolean(
        string='SI SE UTILIZA FORMICA ESPECIAL, CHECAR QUE LA IMAGEN Y EL LINK DE LA PAGINA ESTEN INCLUIDOS. TAMBIEN ESPECIFICAR QUE TIPO DE CUBRE CANTOS SE UTILIZARA',
        copy=False,
    )

    general_f = fields.Boolean(
        string='SI SE COMBINAN LINEAS, ESPECIFICAR QUE JALADERA SE UTILIZARA, CHECAR COLOR',
        copy=False,
    )

    general_g = fields.Boolean(
        string='CHECAR CON EL CLIENTE QUE EL CRISTAL QUE SOLICITA ES EL MISMO QUE LE OFRECEMOS',
        copy=False,
    )

    general_h = fields.Boolean(
        string='VERIFICAR UBICACION DE LAS VENTNAS CUANDO SE UTILIZAN LIBREROS A MURO O HUTCHES',
        copy=False,
    )

    general_i = fields.Boolean(
        string='VERIFICAR QUE EL CLIENTE SEPA CUANDO LA PROFUNDIDAD DE UN ARCHIVERO / PEDESTAL NO ES LA MISMA A LA DE LA CUBIERTA',
        copy=False,
    )

    general_j = fields.Boolean(
        string='SI INCLUYE ELECTRIFICACION CHECAR:',
        copy=False,
    )

    general_k = fields.Boolean(
        string='SI INCLUYE EXTENSION PARA ELECTRIFICACION PONER LA MEDIDA FINAL Y CHECAR QUE ESTE EN LA SECCION DE MAMPARAS Y NO EN POWER PLAN PARA QUE CLAVES LO VEA',
        copy=False,
    )

    station_a = fields.Boolean(
        string='CHECAR QUE LOS ANCHOS DE LAS MAMPARAS EN LAS DESCRIPCIONES COINCIDAN CON LOS ANCHOS DE LOS GAJOS',
        copy=False,
    )

    station_b = fields.Boolean(
        string='CHECAR CANTIDADES DE GAJOS',
        copy=False,
    )

    station_c = fields.Boolean(
        string='ESPECIFICAR CORRECTAMENTE SI EL GAJO ES PINCHABLE O TAPIZADO',
        copy=False,
    )

    station_d = fields.Boolean(
        string='CHECAR QUE SE INCLUYA LAS CONFIGURACIONES DE LAS MAMPARAS (PANEL BUILDER)',
        copy=False,
    )

    station_e = fields.Boolean(
        string='ESPECIFICAR CUANDO UNA MAMPARA LLEVA CLAMPS (PERFORADA/NO PERFORADA)',
        copy=False,
    )

    station_f = fields.Boolean(
        string='CHECAR QUE ESTE BIEN ESPECIFICADO CUANTOS MODULOS SE DEBEN CARGAR',
        copy=False,
    )

    station_g = fields.Boolean(
        string='CHECAR QUE SE HAYA ESPECIFICADO SI LAS CUBIERAS SON HORIZONTALES O VERTICALES',
        copy=False,
    )

    station_h = fields.Boolean(
        string='CHECAR QUE SE HAYA ESPECIFICADO COLOR Y POSICION DE LOS PASACABLES',
        copy=False,
    )

    station_i = fields.Boolean(
        string='CHECAR LOS HERRAJES',
        copy=False,
    )

    station_j = fields.Boolean(
        string='VERIFICAR QUE EL CLIENTE CONOCE LA UBICACION DE LOS KNOCKOUTS O SI REQUIERE MAS',
        copy=False,
    )

    free_a = fields.Boolean(
        string='ESPECIFICAR SI UN ARCHIVERO/PEDESTAL DEBE O NO LLEVAR CUBIERTA',
        copy=False,
    )

    free_b = fields.Boolean(
        string='CHECAR QUE LOS LADOS DE ESCRITORIOS, HERRAJES Y CREDENZAS',
        copy=False,
    )

    free_c = fields.Boolean(
        string='CHECAR QUE EL PEDESTAL/ARCHIVERO NO INTERFIERA CON LA UBICACION DEL PASACABLE',
        copy=False,
    )

    free_d = fields.Boolean(
        string='CHECAR QUE SE HAYA ESPECIFICADO COLOR DE LOS PASACABLES',
        copy=False,
    )

    free_e = fields.Boolean(
        string='CHECAR CON EL CLIENTE SI NECESITA QUE EL PEDESTAL ARCHIVE OFICIO',
        copy=False,
    )

    cost_a = fields.Boolean(
        string='REQUIERE PLANOS',
        copy=False,
    )

    cost_b = fields.Boolean(
        string='PLANOS/DESPIECE',
        copy=False,
    )

    cost_c = fields.Boolean(
        string='CAJA',
        copy=False,
    )

    cost_d = fields.Boolean(
        string='PINTURA Y QUIMICOS',
        copy=False,
    )

    cost_e = fields.Boolean(
        string='DETALLE DE CORTE',
        copy=False,
    )

    cost_f = fields.Boolean(
        string='COINCIDE DETALLE DE CORTE CON PLANO',
        copy=False,
    )

    cost_g = fields.Boolean(
        string='HERRAJES',
        copy=False,
    )

    cost_h = fields.Boolean(
        string='RUTAS DE PRODUCCION',
        copy=False,
    )

    cost_i = fields.Boolean(
        string='TRADUCCION (EXPORTACION)',
        copy=False,
    )

    cost_j = fields.Boolean(
        string='EMPAQUE',
        copy=False,
    )

    cost_k = fields.Boolean(
        string='CFDI',
        copy=False,
    )

    cost_l = fields.Boolean(
        string='PARTIDA ARANCELARIA',
        copy=False,
    )

    cost_m = fields.Boolean(
        string='LA CLAVE CORRESPONDE A LO SOLICITADO',
        copy=False,
    )

    cost_n = fields.Boolean(
        string='DESCRIPCION CORRESPONDE A LOS ACABADOS',
        copy=False,
    )

    cost_o = fields.Boolean(
        string='INVENTARIO',
        copy=False,
    )

    key_a = fields.Boolean(
        string='MEDIDAS GENERALES',
        copy=False,
    )

    key_b = fields.Boolean(
        string='ESPECIFICACIONES',
        copy=False,
    )

    key_c = fields.Boolean(
        string='MATERIALES Y ESPESORES',
        copy=False,
    )

    key_d = fields.Boolean(
        string='ACABADOS',
        copy=False,
    )

    flat_a = fields.Boolean(
        string='MEDIDAS GENERALES',
        copy=False,
    )

    flat_b = fields.Boolean(
        string='EXPLOSIONADO (MOSTRAR COMPONENTES)',
        copy=False,
    )

    flat_c = fields.Boolean(
        string='LISTADO DE COMPONENTES Y HERRAJES',
        copy=False,
    )

    flat_d = fields.Boolean(
        string='CANTIDAD DE COMPONENTES Y HERRAJES',
        copy=False,
    )

    flat_e = fields.Boolean(
        string='TORNILLERIA (CANTIDAD/DESCRIPCION/CLAVE)',
        copy=False,
    )

    flat_f = fields.Boolean(
        string='PIEZAS CON COTAS Y DOBLECES',
        copy=False,
    )

    flat_g = fields.Boolean(
        string='MATERIAL Y CALIBRE',
        copy=False,
    )

    flat_h = fields.Boolean(
        string='MEDIDAS DE CORTE',
        copy=False,
    )

    flat_i = fields.Boolean(
        string='PERFORACIONES PARA DESAGUE',
        copy=False,
    )

    flat_j = fields.Boolean(
        string='CANTIDAD DE PIEZAS',
        copy=False,
    )

    flat_k = fields.Boolean(
        string='POSICION SOLDADURA',
        copy=False,
    )

    wood_a = fields.Boolean(
        string='MEDIDAS GENERALES',
        copy=False,
    )

    wood_b = fields.Boolean(
        string='EXPLOSIONADO (MOSTRAR COMPONENTES)',
        copy=False,
    )

    wood_c = fields.Boolean(
        string='LISTADO DE COMPONENTES Y HERRAJES',
        copy=False,
    )

    wood_d = fields.Boolean(
        string='CANTIDAD DE COMPONENTES Y HERRAJES',
        copy=False,
    )

    wood_e = fields.Boolean(
        string='TORNILLERIA (CANTIDAD/DESCRIPCION/CLAVE)',
        copy=False,
    )

    show_a = fields.Boolean(
        string='NOMBRE DE LA PIEZA',
        copy=False,
    )

    show_b = fields.Boolean(
        string='CANTIDAD',
        copy=False,
    )

    show_c = fields.Boolean(
        string='MATERIAL',
        copy=False,
    )

    show_d = fields.Boolean(
        string='COLOR',
        copy=False,
    )

    show_e = fields.Boolean(
        string='CARAS',
        copy=False,
    )

    show_f = fields.Boolean(
        string='ESPESOR',
        copy=False,
    )

    show_g = fields.Boolean(
        string='MEDIDAS',
        copy=False,
    )

    show_h = fields.Boolean(
        string='SENTIDO DE VENA',
        copy=False,
    )

    show_i = fields.Boolean(
        string='CINTILLA',
        copy=False,
    )

    show_j = fields.Boolean(
        string='TALADROS',
        copy=False,
    )

    show_k = fields.Boolean(
        string='PASACABLES',
        copy=False,
    )

    show_l = fields.Boolean(
        string='PERFORACIONES ESPECIALES (MEDIDA Y UBICACION)',
        copy=False,
    )

    review_ip = fields.Boolean(
        string=u'Revisión IP',
        copy=False,
    )

    note_ip = fields.Char(
        string=u'Motivo de Revisión',
        copy=False,
    )

    review_aip = fields.Boolean(
        string=u'Revisión AIP',
        copy=False,
    )

    note_aip = fields.Char(
        string=u'Motivo de Revisión',
        copy=False,
    )

    review_diseno = fields.Boolean(
        string=u'Revisión Diseño',
        copy=False,
    )

    note_diseno = fields.Char(
        string=u'Motivo de Revisión',
        copy=False,
    )

    date_finished = fields.Datetime(
        string=('Fecha Finalizado'),
        copy=False)

    validation_sc = fields.Selection(
        [('approved', 'Aprobado'),
         ('not_approved', 'No Aprobado')],
        default='not_approved',
        string='Estatus de Validación Servicio al Cliente',
        store=True,
        copy=False,
    )

    validation_time_sc = fields.Datetime(
        string='Fecha de Validación Servicio al Cliente',
        copy=False,
    )

    user_val_sc_id = fields.Many2one(
        'res.users',
        string='Validado por Servicio al Cliente:',
        copy=False,
    )

    task_state_hist_ids = fields.One2many(
        'project.task.stage.hist',
        'task_id',
        string=('Task'),
    )

    task_user_hist_ids = fields.One2many(
        'project.task.user.hist',
        'task_id',
        string=('Task User'),
    )

    is_special = fields.Boolean(
        string='Producto especial',
    )

    # partner_id = fields.Many2one(
    #     'res.partner',
    #     string='Partner'
    # )

    def get_mail_url(self):
        return self.get_share_url()

    def get_share_url(self):
        self.ensure_one()
        params = {
            'model': self._name,
            'res_id': self.id,
        }
        return '/mail/view?' + url_encode(params)

    @api.model
    def create(self, vals):
        res = super(ProjectTask, self).create(vals)
        hist_obj = self.env['project.task.stage.hist']
        hist_user_obj = self.env['project.task.user.hist']

        if res and res.product_id:
            res.force_task_send()

        his_vals = {
            'task_id': res.id,
            'date': fields.Datetime.now(),
            'status_new': res.stage_id.name,
            'user_new': res.user_id.name
        }
        hist_obj.create(his_vals)

        # his_user_vals = {
        #     'task_id': res.id,
        #     'date': fields.Datetime.now(),
        #     'user_new': res.user_id.name
        # }
        # hist_user_obj.create(his_user_vals)

        return res

    @api.multi
    def write(self, vals):
        hist_obj = self.env['project.task.stage.hist']
        newstage = ''
        if 'stage_id' in vals.keys():
            newstage = vals['stage_id']
            task_type = self.env['project.task.type'].browse(newstage)
            his_vals = {
                'task_id': self.id,
                'date': fields.Datetime.now(),
                'status_old': self.stage_id.name,
                'status_new': task_type.name,
                'user_old': self.user_id.name,
                'user_new': self.user_id.name,
            }
            hist_obj.create(his_vals)

        if 'user_id' in vals.keys():
            newuser = vals['user_id']
            user = self.env['res.users'].browse(newuser)
            his_vals = {
                'task_id': self.id,
                'date': fields.Datetime.now(),
                'status_old': self.stage_id.name,
                'status_new': self.stage_id.name,
                'user_old': self.user_id.name,
                'user_new': user.name,
            }
            hist_obj.create(his_vals)

        if 'stage_id' in vals:
            current_stage = self.stage_id
            new_stage_id = vals.get('stage_id')
            new_project_task_type = self.env['project.task.type'].browse(new_stage_id)
            if current_stage.name in ['CLAVE', 'COSTO']:
                if new_project_task_type.name != current_stage.name and \
                   self.validation_ip != 'approved' and self.review_ip is False:
                    raise UserError(_('No puede cambiar de etapa esta tarea si no esta aprobada o marcada la opción de Revisión.'))
                if new_project_task_type.name == 'FINALIZADO' and self.validation_ip != 'approved':
                    raise UserError(_('No puede finalizar esta tarea si no esta aprobada.'))
            if current_stage.name in ['AIP', 'SEMBRADO', 'RENDER']:
                if new_project_task_type.name != current_stage.name and \
                   self.validation_aip != 'approved' and self.review_aip is False:
                    raise UserError(_('No puede cambiar de etapa esta tarea si no esta aprobada o marcada la opción de Revisión.'))
                if new_project_task_type.name == 'FINALIZADO' and self.validation_aip != 'approved':
                    raise UserError(_('No puede finalizar esta tarea si no esta aprobada.'))
            if current_stage.name == u'DISEÑO':
                if new_project_task_type.name != current_stage.name and \
                   self.validation_diseno != 'approved' and self.review_diseno is False:
                    raise UserError(_('No puede cambiar de etapa esta tarea si no esta aprobada o marcada la opción de Revisión.'))
                if new_project_task_type.name == 'FINALIZADO' and self.validation_diseno != 'approved':
                    raise UserError(_('No puede finalizar esta tarea si no esta aprobada.'))
            if current_stage.name == u'SERVICIO AL CLIENTE':
                if new_project_task_type.name != current_stage.name and \
                   self.validation_sc != 'approved':
                    raise UserError(_('No puede cambiar de etapa esta tarea si no esta aprobada.'))
                if new_project_task_type.name == 'FINALIZADO' and self.validation_sc != 'approved':
                    raise UserError(_('No puede finalizar esta tarea si no esta aprobada.'))

        return super(ProjectTask, self).write(vals)

    @api.multi
    def action_task_sent(self):
        """ Open a window to compose an email, with the cfdi invoice template
            message loaded by default
        """

        self.ensure_one()

        mail_tmp_id = self.env.ref(
            'mrp_plm_gebesa.email_template_task_notification', False)

        compose_form = self.env.ref('mail.email_compose_message_wizard_form',
                                    False)

        mail_tmp_id.attachment_ids = self.product_id.attachment_ids and [
            (6, 0, self.product_id.attachment_ids.ids)] or None

        ctx = dict(
            default_model='project.task',
            default_res_id=self.id,
            default_use_template=bool(mail_tmp_id),
            default_template_id=mail_tmp_id.id,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
        )
        return {
            'name': _('Compose task Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def force_task_send(self):
        for task in self:
            email_act = task.action_task_sent()

            if email_act and email_act.get('context'):
                email_ctx = email_act['context']
                email_ctx.update(default_email_from=task.company_id.email)
                try:
                    task.with_context(
                        email_ctx).message_post_with_template(
                        email_ctx.get('default_template_id'))
                except ValueError:
                    raise exceptions.ValidationError(_('Warning'), _(
                        'An error has occurred'))
        return True

    @api.multi
    def send_finish_task_email(self):
        """ Open a window to compose an email, with the cfdi invoice template
            message loaded by default
        """

        if self.stage_id:
            project_task_type = self.stage_id
            if project_task_type.name != 'FINALIZADO':
                raise UserError(_('No puede enviar el correo si la tarea no esta en la etapa FINALIZADA.'))
            self.date_finished = fields.Datetime.now()

        self.ensure_one()
        mail_tmp_id = self.env.ref(
            'mrp_plm_gebesa.email_template_finish_task_notification', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form',
                                    False)
        # mail_tmp_id.attachment_ids = self.product_id.attachment_ids and [
        #     (6, 0, self.product_id.attachment_ids.ids)] or None
        ctx = dict(
            default_model='project.task',
            default_res_id=self.id,
            default_use_template=bool(mail_tmp_id),
            default_template_id=mail_tmp_id.id,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
        )
        return {
            'name': _('Compose task Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }


    @api.multi
    def validation_task_ip(self):
        for rec in self:
            current_stage = self.stage_id
            user_val_id = self.env.user
            if current_stage.name not in ['CLAVE', 'COSTO'] and self.env.user.has_group('mrp_plm_gebesa.group_manager_validation_task_ip'):
                raise UserError(_('No puedes Aprobar esta tarea, no esta en las etapas CLAVE / COSTO.'))
            if user_val_id == rec.user_id:
                raise UserError(_('No puede validar la tarea que tiene asignada.'))
            if not any([rec.cost_a, rec.cost_b, rec.cost_c, rec.cost_d, rec.cost_e, rec.cost_f, rec.cost_g, rec.cost_h,
                       rec.cost_i, rec.cost_j, rec.cost_k, rec.cost_l, rec.cost_m, rec.cost_n, rec.cost_o]):
                raise UserError(_('No puede validar la tarea debe seleccionar al menos una opción del Cheklist.'))
            rec.write({'validation_ip': 'approved'})
            rec.user_val_id = user_val_id
            rec.validation_time_ip = fields.Datetime.now()

        return True

    @api.multi
    def validation_task_aip(self):
        for rec in self:
            current_stage = self.stage_id
            user_val_aip_id = self.env.user
            if current_stage.name not in ['AIP', 'SEMBRADO', 'RENDER'] and self.env.user.has_group('mrp_plm_gebesa.group_manager_validation_task_aip'):
                raise UserError(_('No puedes Aprobar esta tarea, no esta en las etapas AIP / SEMBRADO / RENDER.'))
            # if user_val_aip_id == rec.user_id:
            #     raise UserError(_('No puede validar la tarea que tiene asignada.'))
            if not any([rec.special_a, rec.special_b, rec.special_c, rec.special_d, rec.special_e, rec.special_f, rec.special_g,
                       rec.general_a, rec.general_b, rec.general_c, rec.general_d, rec.general_e, rec.general_f, rec.general_g,
                       rec.general_h, rec.general_i, rec.general_j, rec.general_k, rec.station_a, rec.station_b, rec.station_c,
                       rec.station_d, rec.station_e, rec.station_f, rec.station_g, rec.station_h, rec.station_i, rec.station_j,
                       rec.free_a, rec.free_b, rec.free_c, rec.free_d, rec.free_e]):
                raise UserError(_('No puede validar la tarea debe seleccionar al menos una opción del Cheklist.'))
            rec.write({'validation_aip': 'approved'})
            rec.user_val_aip_id = user_val_aip_id
            rec.validation_time_aip = fields.Datetime.now()

        return True

    @api.multi
    def validation_task_diseno(self):
        for rec in self:
            current_stage = self.stage_id
            user_val_diseno_id = self.env.user
            if current_stage.name != u'DISEÑO' and self.env.user.has_group('mrp_plm_gebesa.group_manager_validation_task_diseno'):
                raise UserError(_(u'No puedes Aprobar esta tarea, no esta en la etapa DISEÑO.'))
            if user_val_diseno_id == rec.user_id:
                raise UserError(_('No puede validar la tarea que tiene asignada.'))
            if not any([rec.key_a, rec.key_b, rec.key_c, rec.key_d, rec.flat_a, rec.flat_b, rec.flat_c, rec.flat_d,
                       rec.flat_e, rec.flat_f, rec.flat_g, rec.flat_h, rec.flat_i, rec.flat_j, rec.flat_k, rec.wood_a,
                       rec.wood_b, rec.wood_c, rec.wood_d, rec.wood_e, rec.show_a, rec.show_b, rec.show_c, rec.show_d,
                       rec.show_e, rec.show_f, rec.show_g, rec.show_h, rec.show_i, rec.show_j, rec.show_k, rec.show_l]):
                raise UserError(_('No puede validar la tarea debe seleccionar al menos una opción del Cheklist.'))
            rec.write({'validation_diseno': 'approved'})
            rec.user_val_diseno_id = user_val_diseno_id
            rec.validation_time_diseno = fields.Datetime.now()

        return True

    @api.multi
    def validation_task_sc(self):
        for rec in self:
            current_stage = self.stage_id
            user_val_sc_id = self.env.user
            if current_stage.name != u'SERVICIO AL CLIENTE' and self.env.user.has_group('mrp_plm_gebesa.group_manager_validation_task_sc'):
                raise UserError(_(u'No puedes Aprobar esta tarea, no esta en la etapa SERVICIO AL CLIENTE.'))
            rec.write({'validation_sc': 'approved'})
            rec.user_val_sc_id = user_val_sc_id
            rec.validation_time_sc = fields.Datetime.now()

        return True
