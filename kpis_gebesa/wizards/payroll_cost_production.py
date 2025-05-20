# Copyright 2022, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class KpiPayrollFamilyProfitWizard(models.TransientModel):
    _name = "kpi.payroll.family.wizard"
    _description = "Kpi Paytoll profit by Product family"

    start_date = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.today
    )

    end_date = fields.Date(
        string='End Date',
        required=True,
        default=fields.Date.today
    )

    account_ids = fields.Many2many(
        'account.account',
        string='Payroll accounts',
        required=True,
    )

    lines_ids = fields.One2many(
        'kpi.payroll.family.det.wizard',
        'kpipayfam_id',
        string='KPI',
    )

    @api.onchange('account_ids')
    def onchange_lines_ids(self):
        for rec in self:
            params = [rec.start_date, rec.end_date]
            acc_ids = rec.account_ids.ids if rec.account_ids else self.env['account.account'].search([]).ids
            params2 = [rec.start_date, rec.end_date, tuple(acc_ids)]
            invoice_data = rec._get_invoicing_amounts(params)
            payroll_data = rec._get_payroll_amounts(tuple(params2))
            detailobj = self.env['kpi.payroll.family.det.wizard']
            linedetobj = self.env['kpi.payroll.analytic']

            orphans = []
            found = []
            # import ipdb; ipdb.set_trace()
            lines = []
            for inv in invoice_data:
                descendants = rec._get_analytic_descendants(inv['cco_id'])
                detdata = detailobj._prepare_det_data(inv, rec.id)
                lines.append((0, 0, detdata))
                # self.lines_ids.append((0, 0, detdata))
                # self.write({'lines_ids': [(0, 0, detdata)]})
                # line = detailobj.create(detdata)
                if descendants[0]['array_agg']:
                    payxinv = filter(lambda pdata: pdata['id'] in descendants[0]['array_agg'], payroll_data)
                    #linedetobj._prepare_det_analytic_data(line.id, payxinv)
                    found.append(descendants[0]['array_agg'])
            # import ipdb; ipdb.set_trace()
            rec.lines_ids = False
            rec.lines_ids = lines
            # rec.write({'lines_ids': lines})
            # rec.update({'lines_ids': lines})


    @api.model
    def _get_invoicing_amounts(self, params=None):
        # import ipdb; ipdb.set_trace()
        query = """
        with invoice as
            (
                select pf.name as familia, pf.id as family_id, aaa.id as cco_id, aaa.code as cco, sum(ail.price_total) as facturacion
                from account_invoice_line ail
                join account_invoice ai on ai.id = ail.invoice_id
                join product_product pp on pp.id = ail.product_id
                join product_template pt on pt.id = pp.product_tmpl_id
                join product_family pf on pf.id = pt.family_id
                join ir_property ipr on ipr.res_id = 'product.family,' || CAST(pf.id AS TEXT) and ipr.name = 'analytic_id' and ipr.type = 'many2one' and ipr.company_id = 1
                join account_analytic_account aaa on aaa.id = CAST(split_part(ipr.value_reference, ',', 2) AS INTEGER)
                where ai.date_invoice >= %s
                and ai.date_invoice <= %s
                and ai.state not in ('cancel', 'draft')
                group by pf.id, aaa.id
            )
            select
              ai.familia
              , ai.family_id
              , ai.cco
              , ai.cco_id
              , round(ai.facturacion, 2) as facturacion
              , round((ai.facturacion / sum(ai.facturacion) over ()) * 100, 2) as percentage
            from invoice as ai
            order by ai.facturacion desc;
        """
        self.env.cr.execute(query, tuple(params))
        return self.env.cr.dictfetchall()

    @api.model
    def _get_payroll_amounts(self, params=None):
        # import ipdb; ipdb.set_trace()
        query = """
        select aaa.id, aaa.code, aaa.name, sum(pil.debit) as sueldos,
            string_agg(aa.id::character varying, ', ' order by aa.id)
            from payroll_import_line pil
            join account_account aa on aa.id = pil.account_id
            join account_analytic_account aaa on aaa.id = pil.analytic_account_id
            join payroll_import pim on pim.id = pil.payroll_id
            where pim.date >= %s
            and pim.date <= %s
            and aa.id in %s
            group by aaa.id;
        """
        self.env.cr.execute(query, tuple(params))
        return self.env.cr.dictfetchall()

    def _get_analytic_descendants(self, analytic_id=None):
        # import ipdb; ipdb.set_trace()
        query = """
            WITH RECURSIVE tree AS (
              SELECT id, ARRAY[]::integer[] AS ancestors
              FROM account_analytic_account WHERE parent_id IS NULL

              UNION ALL

              SELECT account_analytic_account.id, tree.ancestors || account_analytic_account.parent_id
              FROM account_analytic_account, tree
              WHERE account_analytic_account.parent_id = tree.id
            ) SELECT array_agg(id) FROM tree WHERE %s = ANY(tree.ancestors)

        """
        self.env.cr.execute(query, tuple([analytic_id]))
        return self.env.cr.dictfetchall()

    def action_get_data_from_db(self):
        # import ipdb; ipdb.set_trace()
        # params = [self.start_date, self.end_date]
        # params2 = [self.start_date, self.end_date, tuple(self.account_ids.ids)]
        # invoice_data = self._get_invoicing_amounts(params)
        # payroll_data = self._get_payroll_amounts(tuple(params2))
        # detailobj = self.env['kpi.payroll.family.det.wizard']
        # linedetobj = self.env['kpi.payroll.analytic']

        # orphans = []
        # found = []
        # # import ipdb; ipdb.set_trace()
        # lines = []
        # for inv in invoice_data:
        #     descendants = self._get_analytic_descendants(inv['cco_id'])
        #     detdata = detailobj._prepare_det_data(inv, self.id)
        #     lines.append((0, 0, detdata))
        #     # self.lines_ids.append((0, 0, detdata))
        #     # self.write({'lines_ids': [(0, 0, detdata)]})
        #     # line = detailobj.create(detdata)
        #     if descendants[0]['array_agg']:
        #         payxinv = filter(lambda pdata: pdata['id'] in descendants[0]['array_agg'], payroll_data)
        #         #linedetobj._prepare_det_analytic_data(line.id, payxinv)
        #         found.append(descendants[0]['array_agg'])
        # # import ipdb; ipdb.set_trace()
        # self.lines_ids = lines
        # self.write({'lines_ids': lines})
        # self.update({'lines_ids': lines})
        return {
            "type": "ir.actions.do_nothing"
            #'type': 'ir.actions.client',
            #'tag': 'reload',
        }


class KpiPayrollFamilyDetProfitWizard(models.TransientModel):
    _name = "kpi.payroll.family.det.wizard"
    _description = "Kpi Paytoll profit by Product family detail"

    family_id = fields.Many2one(
        'product.family',
        string='Process',
    )

    analytic_id = fields.Many2one(
        'account.analytic.account',
        related='family_id.analytic_id',
        string='CCO',
    )

    cost = fields.Float(
        string='Cost',
    )

    amount = fields.Float(
        string='Invoiced',
    )

    invoced_percent = fields.Float(
        string='Percentage invoiced',
    )

    payroll_analityc_ids = fields.One2many(
        'kpi.payroll.analytic',
        'kpipayfamline_id',
        string='Payroll analytics',
    )

    payroll_amount = fields.Float(
        string='Payroll Amount',
        compute='_compute_payroll_amount'
    )

    kpipayfam_id = fields.Many2one(
        'kpi.payroll.family.wizard',
        string='Header',
    )

    # account_ids = fields.One2many(
    #     'account.account',
    #     'kpipayfamline_id',
    #     string='Accounts',
    # )

    def _prepare_det_data(self, inv=None, header_id=None):
        # import ipdb; ipdb.set_trace()
        return {
            # 'kpipayfam_id': header_id,
            'family_id': self.env['product.family'].browse([inv['family_id']]).id,
            'analytic_id': self.env['account.analytic.account'].browse([inv['cco_id']]).id,
            'amount': inv['facturacion'],
            'invoced_percent': inv['percentage'],
            'cost': 0.00
        }

    @api.depends('payroll_analityc_ids')
    def _compute_payroll_amount(self):
        # import ipdb; ipdb.set_trace()
        for det in self:
            payroll_amount = 0.0
            for payroll in det.payroll_analityc_ids:
                payroll_amount += payroll.proportional_amount
            det.payroll_amount = payroll_amount


class KpiPayrollAnalytic(models.TransientModel):
    _name = "kpi.payroll.analytic"
    _description = "Kpi Payroll profit by Product family detail analytics"

    analytic_id = fields.Many2one(
        'account.analytic.account',
        string='CCO',
    )

    percent = fields.Float(
        string='Percent',
    )

    kpipayfamline_id = fields.Many2one(
        'kpi.payroll.family.det.wizard',
        string='Kpi line',
    )

    total = fields.Float(
        string='Analytic total',
    )

    proportional_amount = fields.Float(
        string='Amount',
        compute='_compute_proportional_amount'
    )

    @api.depends('percent', 'total')
    def _compute_payroll_amount(self):
        # import ipdb; ipdb.set_trace()
        for det in self:
            det.proportional_amount = det.total * (det.percent / 100)

    def _prepare_det_analytic_data(self, line_id=None, data=None):
        # import ipdb; ipdb.set_trace()
        for det in data:
            self.env['kpi.payroll.analytic'].create({
                'kpipayfamline_id': line_id,
                'analytic_id': self.env['account.analytic.account'].browse([det['id']]).id,
                'percent': 100,
                'total': det['sueldos']
            })


# class KpiPayrollAccount(models.TransientModel):
#     _name = "kpi.payroll.account"
#     _description = "Kpi Payroll profit by Product family detail analytics"

#     account_id = fields.Many2one(
#         'account.account',
#         string='CCO',
#     )

#     kpipayfamline_id = fields.Many2one(
#         'kpi.payroll.family.det.wizard',
#         string='Kpi line',
#     )
