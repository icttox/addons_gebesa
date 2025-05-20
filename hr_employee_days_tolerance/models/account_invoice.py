# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
import pytz
from odoo import _, api, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_move_create(self):
        """ Create the movements to the given date,
        according to the days of tolerance granted to the user"""
        if self:
            employee = self.env['hr.employee'].sudo().search(
                [('user_id', '=', self._uid)])
            if not employee:
                raise UserError(_('You do not have an assigned employee.\n Please \
                                contact your system administrator'))
            employee_days = employee[0].tolerance_days

            for inv in self:
                if inv.date_invoice is not False:
                    date_today = datetime.today()
                    timezone = pytz.timezone(self._context.get('tz') or 'UTC')
                    fecha_tolerancia = pytz.UTC.localize(date_today)
                    fecha_tolerancia = fecha_tolerancia.astimezone(timezone)
                    fecha_tolerancia = fecha_tolerancia.date()
                    day_tole_res = fecha_tolerancia - timedelta(
                        days=employee_days)
                    days_tol = str(day_tole_res)
                    date_tol = datetime.strptime(days_tol, '%Y-%m-%d').date()

                    if inv.date_invoice < date_tol:
                        date_tol = day_tole_res.strftime('%d-%m-%Y')
                        raise UserError(_('You can not bill! \
                                        The date may not be earlier \
                                        than %s .') % date_tol)

        return super().action_move_create()


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post(self, invoice=False):

        employee = self.env['hr.employee'].sudo().search(
            [('user_id', '=', self._uid)])
        if not employee:
            raise UserError(_('You do not have an assigned employee.\n Please \
                            contact your system administrator'))
        employee_days = employee[0].tolerance_days

        for move in self:
            date_today = datetime.today()
            timezone = pytz.timezone(self._context.get('tz') or 'UTC')
            fecha_tolerancia = pytz.UTC.localize(date_today)
            fecha_tolerancia = fecha_tolerancia.astimezone(timezone)
            fecha_tolerancia = fecha_tolerancia.date()
            day_tole_res = fecha_tolerancia - timedelta(
                days=employee_days)
            days_tol = str(day_tole_res)
            date_tol = datetime.strptime(days_tol, '%Y-%m-%d').date()

            if move.date < date_tol:
                date_tol = day_tole_res.strftime('%d-%m-%Y')
                raise UserError(_('You can post a move \
                                with date earlier \
                                than %s .') % date_tol)
        return super().post(invoice)
