# -*- coding: utf-8 -*-

from json.decoder import JSONDecodeError
from odoo import models, fields, api
import requests


class GitCommit(models.Model):
    _inherit = "project.git.commit"

    authored_date = fields.Datetime(
        string='Authored Date',
    )

    short_id = fields.Char(
        string='Short Id',
    )

    author_name = fields.Char(
        string='Author Name',
    )

    author_email = fields.Char(
        string='Author Email',
    )

    committer_name = fields.Char(
        string='Committer Name',
    )

    committer_email = fields.Char(
        string='Committer Email',
    )

    additions = fields.Integer(
        string='Aditions',
    )

    deletions = fields.Integer(
        string='Deletions',
    )

    total = fields.Integer(
        string='Total',
    )

    diff = fields.Text(
        string='Diff',
    )

    new_path = fields.Char(
        string='New Path',
    )

    old_path = fields.Char(
        string='New Path',
    )

    new_file = fields.Boolean(
        string='New File',
    )

    renamed_file = fields.Boolean(
        string='Renamed File',
    )

    deleted_file = fields.Boolean(
        string='Deleted File',
    )

    @api.multi
    def _call_gitlab_api_commit_diff(self):
        for commit in self:
            url = ''.join(('http://gitlab.e-fector.com/api/v4/projects/', str(
                commit.repository_id.internal_id), '/repository/commits/',
                commit.name, '/diff'))
            headers = {
                'Content-Type': 'text/xml',
                'PRIVATE-TOKEN': commit.repository_id.private_token}
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
    def get_diff(self):
        for commit in self:
            vals = commit._call_gitlab_api_commit_diff()
            for element in vals:
                diff = element.get('diff')
                new_path = element.get('new_path')
                old_path = element.get('old_path')
                new_file = element.get('new_file')
                renamed_file = element.get('renamed_file')
                deleted_file = element.get('deleted_file')
                commit.write({
                    'diff': diff,
                    'new_path': new_path,
                    'old_path': old_path,
                    'new_file': new_file,
                    'renamed_file': renamed_file,
                    'deleted_file': deleted_file
                })
