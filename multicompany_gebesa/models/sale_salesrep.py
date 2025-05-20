# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models, fields
from odoo.exceptions import UserError


class SaleSalesrep(models.Model):
    _name = 'sale.salesrep'
    _description = 'descripcion pendiente'

    name = fields.Char(
        string='Name',
    )
    Commission_ids = fields.One2many(
        'sale.salesrep.commission',
        'salesrep_id',
        string='Commissions',
    )
    salesrep_ids = fields.Many2many(
        'res.users',
        string='Vendedores',
    )
    salesrep_type = fields.Selection(
        [('normal', 'Normal'),
         ('strategic', 'Strategic')],
        string="Salesrep type",
        default='normal',
    )
    team_id = fields.Many2one(
        'crm.team',
        string='Canal',
        company_dependent=True
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )


class SaleSalesrepCommission(models.Model):
    _name = 'sale.salesrep.commission'
    _description = 'descripcion pendiente'

    salesrep_id = fields.Many2one(
        'sale.salesrep',
        string='REP',
    )
    start_date = fields.Date(
        string='Start date'
    )
    end_date = fields.Date(
        string='End Date'
    )
    commission = fields.Float(
        string='Commission',
    )

    @api.constrains('salesrep_id', 'start_date', 'end_date')
    def _check_unique_name_company(self):
        for commission in self:
            commission_ids = self.search([
                ('salesrep_id', '=', commission.salesrep_id.id),
                ('start_date', '<=', commission.start_date),
                ('end_date', '>=', commission.start_date),
                ('id', '!=', commission.id)])
            commission_ids2 = self.search([
                ('salesrep_id', '=', commission.salesrep_id.id),
                ('start_date', '<=', commission.end_date),
                ('end_date', '>=', commission.end_date),
                ('id', '!=', commission.id)])
            if commission_ids or commission_ids2:
                raise UserError(
                    _("The date range of this commission overlaps the range of \
                    another commission,\nplease check the dates"))
