# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
import pytz
from odoo import _, models, api
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def post(self):
        """ Create the movements to the given date,
        according to the days of tolerance granted to the user"""
        employee = self.env['hr.employee'].sudo().search(
            [('user_id', '=', self._uid)])
        if not employee:
            raise UserError(_('You do not have an assigned employee.\n Please \
                            contact your system administrator'))
        employee_days = employee[0].tolerance_days

        for rec in self:
            if rec.payment_date is not False:
                date_today = datetime.today()
                timezone = pytz.timezone(self._context.get('tz') or 'UTC')
                fecha_tolerancia = pytz.UTC.localize(date_today)
                fecha_tolerancia = fecha_tolerancia.astimezone(timezone)
                fecha_tolerancia = fecha_tolerancia.date()
                day_tole_res = fecha_tolerancia - timedelta(days=employee_days)
                days_tol = str(day_tole_res)

                if rec.payment_date < day_tole_res:
                    days_tol = day_tole_res.strftime('%d-%m-%Y')
                    raise UserError(_('Error! \
                                    The date may not be earlier \
                                    than %s .') % days_tol)

        return super(AccountPayment, self).post()
