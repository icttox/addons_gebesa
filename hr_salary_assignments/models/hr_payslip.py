from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    salary_assing_ids = fields.One2many(
        'hr.salary.assingments', 'slip_id')
    refund_payslip_id = fields.Many2one(
        'hr.payslip',
        string="Payslip for which this payslip is the credit note",
        help="Indicates this payslip is a refund of another")

    filtered_line_ids = fields.One2many(
        'hr.payslip.line',
        string='Payslip Lines',
        compute='_compute_filtered_line_ids'
    )

    @api.depends('line_ids')
    def _compute_filtered_line_ids(self):
        for slip in self:
            slip.filtered_line_ids = slip.line_ids.filtered('salary_rule_id.show_in_payslip')

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.salary_assing_ids.write({'state': 'reserved'})
        return res

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            rec.salary_assing_ids.write({'state': 'reserved'})
        return res

    def compute_sheet(self):
        """
        overwrites compute sheet for adds
        functionality of salary assign and refund payslip
        Returns:
            Bool
        """
        for payslip in self:
            number = payslip.number or self.env['ir.sequence'].next_by_code(
                'salary.slip')
            if payslip.refund_payslip_id:
                payslip.line_ids.unlink()
                list_pl = []
                list_pl = [line.copy()
                           for line in payslip.refund_payslip_id.line_ids]
                lines = [(4, line.id) for line in list_pl]
                payslip.write(
                    {
                        'line_ids': lines,
                        'number': number
                    })
                continue
            salary_lines = payslip.prepare_payslip_lines()

            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply should be
            # for all current contracts of the employee
            payslip.line_ids.unlink()
            payslip.write({'line_ids': salary_lines})
            contract_ids = payslip.contract_id.ids or \
                payslip.employee_id._get_contracts(payslip.date_from, payslip.date_to).ids
            lines = [(0, 0, line) for line in self._get_slip_lines(contract_ids, payslip.id)]
            payslip.write({'line_ids': lines, 'number': number})
            salary_lines = payslip.get_line_salary_assing()
            payslip.salary_assing_ids = [(4, sal.id) for sal in salary_lines]
        return True

    # def refund_sheet(self):
        """
        Generate Pay Slip Refund
        Returns:
            Payslip refund view
        """
        if any(self.filtered(lambda payslip: payslip.credit_note)):
            raise ValidationError(_("Payslip not must be Refund."))
        for payslip in self:
            copied_payslip = payslip.copy(
                {'credit_note': True,
                 'name': _('Refund: ') + payslip.name,
                 'refund_payslip_id': payslip.id})
            refund_salary_lines = payslip.get_refund_line_salary_assing()
            copied_payslip.salary_assing_ids = [(4, sal.id) for sal in refund_salary_lines]
            copied_payslip.action_payslip_done()
        formview_ref = self.env.ref('hr_payroll.view_hr_payslip_form', False)
        treeview_ref = self.env.ref('hr_payroll.view_hr_payslip_tree', False)
        return {
            'name': ("Refund Payslip"),
            'view_mode': 'tree, form',
            'view_id': False,
            'res_model': 'hr.payslip',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('id', 'in', %s)]" % copied_payslip.ids,
            'views': [
                (treeview_ref and treeview_ref.id or False, 'tree'),
                (formview_ref and formview_ref.id or False, 'form')],
            'context': {}
        }

    def get_refund_line_salary_assing(self):
        """
        Generate salary assings for Payslip Refund
        Returns:
            refund salary assings list
        """
        refund_salary_assings = []
        for salary_assing in self.salary_assing_ids:
            copied_salary_assing = salary_assing.copy(
                {'credit_note': True,
                 'slip_id': False,
                 'state': 'draft'})
            refund_salary_assings.append(copied_salary_assing)
        return refund_salary_assings

    def get_line_salary_assing(self):
        """
        Search salary assings
        Returns:
            Salary assings list excluding the credit note
        """
        salary_assing = self.env['hr.salary.assingments']
        domain = [
            ('credit_note', '!=', True),
            ('date_paid', '>=', self.date_from),
            ('date_paid', '<=', self.date_to),
            ('state', '=', 'validated'),
            ('employee_id', '=', self.employee_id.id),
            ('contract_id', '=', self.contract_id.id),
            ('salary_rule_id', 'in', self.struct_id.rule_ids.ids),
        ]
        return salary_assing.search(domain)

    def prepare_payslip_lines(self):
        res = []
        for line in self.salary_assing_ids:
            vals = {
                'name': line.salary_rule_id.name,
                'code': line.code,
                'salary_rule_id': line.salary_rule_id.id,
                'category_id': line.category_id.id,
                'slip_id': line.slip_id.id,
                'employee_id': line.employee_id.id,
                'contract_id': line.contract_id.id,
                'rate': line.rate,
                'amount': line.amount,
                'quantity': line.quantity,
                'total': line.total,
                'note': line.note,
                'sequence': line.sequence,
            }
            res.append((0, 0, vals))
        return res

    @api.onchange('employee_id', 'date_from', 'date_to', 'contract_id')
    def onchange_salary_assings(self):
        fields_constrains = [
            'employee_id', 'date_from', 'date_to', 'contract_id', 'struct_id']
        for record in self:
            validate_field = [
                getattr(record, f) for f in fields_constrains]
            if not all(validate_field):
                continue
            salary_lines = record.get_line_salary_assing()
            record.salary_assing_ids = [(6, 0, salary_lines.ids)]

    def action_payslip_cancel(self):
        res = super().action_payslip_cancel()
        self.mapped('salary_assing_ids').write({'state': 'validated'})
        return res

    def action_payslip_done(self):
        res = super().action_payslip_done()
        self.mapped('salary_assing_ids').write({'state': 'paid'})
        return res

    def unlink(self):
        self.mapped('salary_assing_ids').write({'state': 'validated'})
        return super().unlink()

    @api.model
    def _get_slip_lines(self, contract_ids, payslip_id):  # pylint: disable=R1260
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(
                    localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = (
                localdict['categories'].dict[category.code] + amount
                if category.code in localdict['categories'].dict
                else amount
            )
            return localdict

        class BrowsableObject(object):  # pylint: disable=R0205
            def __init__(self, employee_id, dict_group, env):
                self.employee_id = employee_id
                self.dict = dict_group
                self.env = env

            def __getattr__(self, attr):
                return self.dict.__getitem__(attr) if attr in self.dict else 0.0

        class InputLine(BrowsableObject):
            """a class that will be used into the python code,
            mainly for usability purposes
            """
            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute(
                    """SELECT sum(amount) as sum
                   FROM hr_payslip as hp, hr_payslip_input as pi
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND
                    hp.id = pi.payslip_id AND pi.code = %s""",
                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()[0] or 0.0

        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code, mainly for
            usability purposes
            """
            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute(
                    """SELECT sum(number_of_days) as number_of_days,
                    sum(number_of_hours) as number_of_hours
                    FROM hr_payslip as hp, hr_payslip_worked_days as pi
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND
                    hp.id = pi.payslip_id AND pi.code = %s""",
                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res[0] if res else 0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res[1] if res else 0

        class Payslips(BrowsableObject):
            """a class that will be used into the python code, mainly for
            usability purposes
            """
            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute(
                    """SELECT sum(case when hp.credit_note = False then
                    (pl.total) else (-pl.total) end)
                    FROM hr_payslip as hp, hr_payslip_line as pl
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND
                    hp.id = pl.slip_id AND pl.code = %s""",
                    (self.employee_id, from_date, to_date, code))
                res = self.env.cr.fetchone()
                return res[0] if res else 0.0

        # we keep a dict with the result because a value can be overwritten
        # by another rule with the same code

        result_dict = {}
        rules_dict = {}
        worked_days_dict = {}
        inputs_dict = {}
        blacklist = []
        assing_totals = {
            line.code: line.total for line in self.salary_assing_ids
        }
        payslip = self.env['hr.payslip'].browse(payslip_id)
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days_dict[worked_days_line.code] = worked_days_line
        for input_line in payslip.input_line_ids:
            inputs_dict[input_line.code] = input_line

        categories = BrowsableObject(payslip.employee_id.id, {}, self.env)
        inputs = InputLine(payslip.employee_id.id, inputs_dict, self.env)
        worked_days = WorkedDays(payslip.employee_id.id, worked_days_dict,
                                 self.env)
        payslips = Payslips(payslip.employee_id.id, payslip, self.env)
        rules = BrowsableObject(payslip.employee_id.id, rules_dict, self.env)
        for line in self.mapped('salary_assing_ids'):
            if line.category_id.code not in categories.dict:
                categories.dict[line.category_id.code] = 0.00
            categories.dict[line.category_id.code] += line.total
        baselocaldict = {'categories': categories, 'rules': rules,
                         'payslip': payslips, 'worked_days': worked_days,
                         'inputs': inputs}
        contracts = self.env['hr.contract'].browse(contract_ids)
        rule_ids = payslip.struct_id.rule_ids

        for contract in contracts:
            employee = contract.employee_id
            localdict = dict(baselocaldict, employee=employee,
                             contract=contract)
            for rule in rule_ids:
                key = rule.code + '-' + str(contract.id)
                localdict['result'] = None
                localdict['result_qty'] = 1.0
                localdict['result_rate'] = 100
                # check if the rule can be applied
                if rule._satisfy_condition(localdict) and rule.id not in \
                        blacklist:
                    # compute the amount of the rule
                    amount, qty, rate = rule._compute_rule(localdict)
                    # check if there is already a rule computed with that code
                    previous_amount = localdict[rule.code] if rule.code in localdict else 0.0
                    # set/overwrite the amount computed for this rule in the
                    # localdict
                    total_assing = assing_totals.get(rule.code)
                    tot_rule = total_assing or (amount * qty * rate / 100.0)
                    localdict[rule.code] = tot_rule
                    rules_dict[rule.code] = rule
                    if total_assing:
                        continue
                    # sum the amount for its salary category
                    localdict = _sum_salary_rule_category(
                        localdict, rule.category_id,
                        tot_rule - previous_amount)
                    # create/overwrite the rule in the temporary results
                    result_dict[key] = {
                        'salary_rule_id': rule.id,
                        'contract_id': contract.id,
                        'name': rule.name,
                        'code': rule.code,
                        'category_id': rule.category_id.id,
                        'sequence': rule.sequence,
                        'appears_on_payslip': rule.appears_on_payslip,
                        'amount_select': rule.amount_select,
                        'amount_fix': rule.amount_fix,
                        'amount_percentage': rule.amount_percentage,
                        'amount': amount,
                        'employee_id': contract.employee_id.id,
                        'quantity': qty,
                        'rate': rate,
                    }
        return list(result_dict.values())
