
from json.decoder import JSONDecodeError
from odoo import fields, api, models
from odoo.tools import pycompat
import requests


class ProjectGitGitlabWizards(models.TransientModel):
    _name = 'project.git.gitlab.wizards'

    fecha_ini = fields.Datetime(
        string='Fecha Inicial'
    )
    fecha_fin = fields.Datetime(
        string='Fecha Final'
    )

    repository_id = fields.Many2one(
        'project.git.repository',
        string='Repository'
    )

    @api.multi
    def _call_gitlab_api_commit(self, cont):
        for com in self:
            timezone = self._context.get('tz')
            timezone = pycompat.to_native(timezone)
            self_tz = self.with_context(tz=timezone)
            fecha_ini = fields.Datetime.context_timestamp(self_tz, com.fecha_ini)
            fecha_fin = fields.Datetime.context_timestamp(self_tz, com.fecha_fin)
            since = fecha_ini.strftime("%Y-%m-%dT%H:%M")
            until = fecha_fin.strftime("%Y-%m-%dT%H:%M")
            url = ''.join(('http://gitlab.e-fector.com/api/v4/projects/', str(
                com.repository_id.internal_id), '/repository/commits?since=', str(
                since), '&until=', str(until), '&all=', str(True), '&page=', str(cont),
                '&with_stats=True&first_parent=True'))

            headers = {
                'Content-Type': 'text/xml',
                'PRIVATE-TOKEN': com.repository_id.private_token}
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
            cont = 0
            repetir_while = True
            while repetir_while:
                vals = comm._call_gitlab_api_commit(cont)
                if not vals:
                    repetir_while = False
                else:
                    comm._create_commits(vals)
                cont = cont + 1

    @api.multi
    def _create_commits(self, vals):
        for element in vals:
            id = element.get('id')
            message = element.get('message')

            if 'merge' in message:
                continue

            title = element.get('title')
            web_url = element.get('web_url')
            author_name = element.get('author_name')
            author_email = element.get('author_email')
            committer_name = element.get('committer_name')
            committer_email = element.get('committer_email')
            short_id = element.get('short_id')
            authored_date = element.get('authored_date')
            committed_date = element.get('committed_date')
            additions = deletions = total = 0
            if element.get('stats'):
                stats = element.get('stats')
                additions = stats.get('additions')
                deletions = stats.get('deletions')
                total = stats.get('total')

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
                ('repository_id', '=', self.repository_id.id),
                ('default', '=', True),
            ])

            if not commit:
                commit = self.env['project.git.commit'].create({
                    'name': id,
                    'message': message,
                    'branch_id': branch.id,
                    'message_short': title,
                    'url': web_url,
                    'author_id': autor.id,
                    'repository_id': self.repository_id.id,
                    'author_name': author_name,
                    'author_email': author_email,
                    'committer_name': committer_name,
                    'committer_email': committer_email,
                    'short_id': short_id,
                    'authored_date': authored_date,
                    'additions': additions,
                    'deletions': deletions,
                    'total': total,
                    'type': 'gitlab',
                    'date': committed_date})

                commit.get_diff()
