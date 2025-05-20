# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    collection_manager_id = fields.Many2one(
        'res.users',
        string=_(u'Collection manager'),
    )
