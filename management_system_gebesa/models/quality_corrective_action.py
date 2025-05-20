# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import UserError
from odoo import models, fields, api


class QualityCorrectiveAction(models.Model):
    _name = 'quality.corrective.action'
    _rec_name = 'folio'
    _inherit = ['message.post.show.all']
    _description = 'descripcion pendiente'

    date = fields.Date(
        default=fields.Date.context_today,
    )

    folio = fields.Char(
        string='Folio de AC',
    )

    motive = fields.Selection(
        [('audit_internal', 'Audit internal'),
         ('audit_external', 'Audit external'),
         ('process', 'Proceso'),
         ('indicator', 'Indicator'),
         ('other', 'Other'), ],
        string='Motive',
        default='process',
        required=True,
    )

    other = fields.Char(
        string='Other',
    )

    departament_id = fields.Many2one(
        'hr.department',
        string='Department',
    )

    responsible_id = fields.Many2one(
        'hr.employee',
        string='Name responsible',
        required=True,
    )

    description = fields.Text(
        string='Description',
    )

    action_line_ids = fields.One2many(
        'quality.contingent.actions',
        'corrective_action_id',
        string='Contingent actions',
    )

    why = fields.Text(
        string='¿Why?',
    )

    why_1 = fields.Text(
        string='¿Why?',
    )

    why_2 = fields.Text(
        string='¿Why?',
    )

    why_3 = fields.Text(
        string='¿Why?',
    )

    why_4 = fields.Text(
        string='¿Why?',
    )

    cause_root = fields.Text(
        string='Root cause',
    )

    corrective_actions_ids = fields.One2many(
        'quality.corrective.action.lines',
        'corrective_action_id',
        string='Corrective action lines',
    )

    exist = fields.Boolean(
        string='There are similar nonconformities',
    )

    requer = fields.Boolean(
        string='Requires updating of risks and opportunities',
    )

    change = fields.Boolean(
        string='Changes to the SGC (documents, indicators, etc.)',
    )

    indicate = fields.Text(
        string='Indicate',
    )

    indicate_1 = fields.Text(
        string='Indicate',
    )

    indicate_2 = fields.Text(
        string='Indicate',
    )

    check_id = fields.Many2one(
        'hr.employee',
        string='Check',
    )

    status = fields.Selection(
        [('open', 'Abierto'),
         ('process', 'Proceso'),
         ('closed', 'Cerrado')],
        string='Status',
        default='open',
    )

    revised_id = fields.Many2one(
        'hr.employee',
        string='Revised',
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )

    qty_attachments = fields.Integer(
        "Attachments",
        compute="count_attachments",
        store=False,
        help='Number of attachments for acction corrective')

    @api.one
    def count_attachments(self):
        obj_attachment = self.env['ir.attachment']
        self.qty_attachments = obj_attachment.search_count(
            [('res_model', '=', 'quality.corrective.action'),
             ('res_id', '=', self.id,)])

    @api.model
    def create(self, vals_list):
        vals_list['folio'] = self.env['ir.sequence'].next_by_code(
            'quality.corrective.action') or '/'
        return super().create(vals_list)

    @api.multi
    def action_process(self):
        for corrective in self:
            corrective.status = 'process'
            if corrective.status == 'process':
                corrective.process = True
            return True

    @api.multi
    def action_closed(self):
        for corrective in self:
            corrective.status = 'closed'
            if not corrective.qty_attachments or corrective.qty_attachments == 0:
                raise UserError(('¡Necesitas adjuntar evidencia de la acción correctiva!'))
            if corrective.qty_attachments >= 1:
                corrective.process = False
            return True

    @api.multi
    def send_acction_corrective_email(self):
        self.ensure_one()
        mail_tmp_id = self.env.ref(
            'management_system_gebesa.email_corrective_actions_notification', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form',
                                    False)

        ctx = dict(
            default_model='quality.corrective.action',
            default_res_id=self.id,
            default_use_template=bool(mail_tmp_id),
            default_template_id=mail_tmp_id.id,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
        )
        return {
            'name': ('Compose Action Corrective Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
