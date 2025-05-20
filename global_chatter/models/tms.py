# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class TmsRoute(models.Model):
    _name = 'tms.route'
    _inherit = ['message.post.show.all', 'tms.route']


class TmsRouteTollstation(models.Model):
    _name = 'tms.route.tollstation'
    _inherit = ['message.post.show.all', 'tms.route.tollstation']
