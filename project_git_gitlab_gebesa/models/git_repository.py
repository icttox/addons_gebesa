# -*- coding: utf-8 -*-

from json.decoder import JSONDecodeError
from odoo import models, fields, api
import requests


class GitRepository(models.Model):
    _inherit = "project.git.repository"

    internal_id = fields.Integer(
        string='Internal Id'
    )

    private_token = fields.Char(
        string='Private Token'
    )

    @api.multi
    def _call_gitlab_api_branch(self):
        for rep in self:
            url = ''.join(('http://gitlab.e-fector.com/api/v4/projects/', str(
                rep.internal_id), '/repository/branches'))
            headers = {
                'Content-Type': 'text/xml',
                'PRIVATE-TOKEN': rep.private_token}
            try:
                response = requests.get(
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

            if hasattr(response_json, 'get'):
                response_json = []
            return response_json

    @api.multi
    def action_get_branches(self):
        for repo in self:
            vals = repo._call_gitlab_api_branch()
            repo._create_branches(vals)

    @api.multi
    def _create_branches(self, vals):
        for element in vals:
            name = element.get('name')
            web_url = element.get('web_url')
            merged = element.get('merged')
            protected = element.get('protected')
            developers_can_push = element.get('developers_can_push')
            developers_can_merge = element.get('developers_can_merge')
            can_push = element.get('can_push')
            default = element.get('default')

            branch = self.env['project.git.branch'].search([
                ('name', '=', name)
            ])
            if not branch:
                self.env['project.git.branch'].create({
                    'name': name,
                    'url': web_url,
                    'merged': merged,
                    'protected': protected,
                    'developers_can_push': developers_can_push,
                    'developers_can_merge': developers_can_merge,
                    'repository_id': self.id,
                    'can_push': can_push,
                    'type': 'gitlab',
                    'default': default})

    @api.multi
    def _call_gitlab_api_commit(self):
        for com in self:
            url = ''.join(('http://gitlab.e-fector.com/api/v4/projects/', str(
                com.internal_id), '/repository/commits'))
            headers = {
                'Content-Type': 'text/xml',
                'PRIVATE-TOKEN': com.private_token}
            try:
                response = requests.get(
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

            if hasattr(response_json, 'get'):
                response_json = []
            return response_json

    @api.multi
    def action_get_commits(self):
        for comm in self:
            vals = comm._call_gitlab_api_commit()
            comm._create_commits(vals)

    @api.multi
    def _create_commits(self, vals):
        for element in vals:
            id = element.get('id')
            message = element.get('message')
            title = element.get('title')
            web_url = element.get('web_url')
            author_name = element.get('author_name')
            author_email = element.get('author_email')
            committer_name = element.get('committer_name')
            committer_email = element.get('committer_email')
            short_id = element.get('short_id')
            authored_date = element.get('authored_date')
            committed_date = element.get('committed_date')

            autor = self.env['project.git.user'].search([
                ('email', '=', author_email)
            ])
            if not autor:
                autor = self.env['project.git.user'].create({
                    'name': author_name,
                    'username': author_name,
                    'email': author_email,
                    'type': 'gitlab',
                })

            commit = self.env['project.git.commit'].search([
                ('name', '=', id)
            ])

            branch = self.env['project.git.branch'].search([
                ('repository_id', '=', self.id),
                ('default', '=', True),
            ])

            if not commit:
                self.env['project.git.commit'].create({
                    'name': id,
                    'message': message,
                    'branch_id': branch.id,
                    'message_short': title,
                    'url': web_url,
                    'author_id': autor.id,
                    'repository_id': self.id,
                    'author_name': author_name,
                    'author_email': author_email,
                    'committer_name': committer_name,
                    'committer_email': committer_email,
                    'short_id': short_id,
                    'authored_date': authored_date,
                    'type': 'gitlab',
                    'date': committed_date})

    @api.multi
    def _call_gitlab_api_user(self):
        for use in self:
            url = 'http://gitlab.e-fector.com/api/v4/users'
            headers = {
                'Content-Type': 'text/xml',
                'PRIVATE-TOKEN': use.private_token}
            try:
                response = requests.get(
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

            if hasattr(response_json, 'get'):
                response_json = []
            return response_json

    @api.multi
    def action_get_users(self):
        for us in self:
            vals = us._call_gitlab_api_user()
            us._create_users(vals)

    @api.multi
    def _create_users(self, vals):
        for element in vals:
            name = element.get('name')
            username = element.get('username')
            email = element.get('email')
            id = element.get('id')
            web_url = element.get('web_url')
            avatar_url = element.get('avatar_url')

            user = self.env['project.git.user'].search([
                ('name', '=', name)
            ])
            if not user:
                self.env['project.git.user'].create({
                    'name': name,
                    'username': username,
                    'email': email,
                    'uuid': id,
                    'avatar': avatar_url,
                    'type': 'gitlab',
                    'url': web_url})
