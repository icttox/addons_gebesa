# -*- coding: utf-8 -*-

from json.decoder import JSONDecodeError
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests


class ProjectTask(models.Model):
    _inherit = "project.task"

    issue = fields.Char(
        string='Issue',
    )

    @api.multi
    def call_gitlab_api_task(self):
        for tas in self:
            repositorio = self.env['project.git.repository'].search([
                ('project_id', '=', tas.project_id.id)
            ])
            if not repositorio:
                raise UserError(_("No tiene un repositorio asignado."))
            if not tas.user_id:
                raise UserError(_("La tarea no tiene un usuario asignado."))
            user = self.env['project.git.user'].search([
                ('odoo_user', '=', tas.user_id.id)
            ])
            if not user:
                raise UserError(_("No tiene un usuario asignado."))

            var = tas.tag_ids.mapped('name')
            tags = ','.join(tag for tag in var)
            # descr = html2plaintext(tas.description).replace('\n', '') if (
            #     tas.description) else 'Sin descripción'
            descr = tas.description if (tas.description) else 'Sin descripción'
            url = ''.join(('http://gitlab.e-fector.com/api/v4/projects/', str(
                repositorio.internal_id), '/issues?title=', str(
                tas.name), '&labels=', str(tags), '&description=', str(
                descr), '&assignee_ids=', str(user.uuid)))
            headers = {
                'Content-Type': 'text/xml',
                'PRIVATE-TOKEN': repositorio.private_token}
            try:
                response = requests.post(
                    url, headers=headers, verify=True, timeout=20)
                response.raise_for_status()
                response_json = response.json()
            except requests.exceptions.RequestException as req_e:
                return [{'status': 'error', 'message': str(req_e)}]
            except requests.exceptions.HTTPError as res_e:
                msg = str(res_e)
                return [{'status': 'error', 'message': msg}]
            except JSONDecodeError as err:
                return [{'status': 'error', 'message': str(err)}]

            if 'web_url' in response_json:
                tas.issue = response_json['web_url']

            if hasattr(response_json, 'post'):
                response_json = []
            return response_json

    # @api.multi
    # def action_get_tasks(self):
    #     for task in self:
    #         vals = task._call_gitlab_api_task()
