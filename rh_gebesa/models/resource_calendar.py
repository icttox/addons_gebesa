# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    active = fields.Boolean(
        string='Active',
        default=True,
    )

    starting_day = fields.Selection(
        [('lunes', 'Lunes'),
         ('martes', 'Martes'),
         ('miercoles', 'Miercoles'),
         ('jueves', 'Jueves'),
         ('viernes', 'Viernes'),
         ('sabado', 'Sabado'),
         ('domingo', 'Domingo')],
        string='Starting Day',
        default='lunes',
    )

    finish_day = fields.Selection(
        [('lunes', 'Lunes'),
         ('martes', 'Martes'),
         ('miercoles', 'Miercoles'),
         ('jueves', 'Jueves'),
         ('viernes', 'Viernes'),
         ('sabado', 'Sabado'),
         ('domingo', 'Domingo')],
        string='Finish Day',
        default='viernes',
    )

    start_hour = fields.Float(
        string='Start Hour',
        help="Start of working hour.\n",
        default=8,
    )

    finish_hour = fields.Float(
        string='Finish Hour',
        help="End of working hour.\n",
        default=18,
    )

    break_time = fields.Float(
        string='Break Time',
        default=0.5,
    )
