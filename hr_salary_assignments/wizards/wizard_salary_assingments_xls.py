from odoo import api, fields, models, _
from odoo.tools import pycompat
import base64
import logging
import psycopg2
import itertools
import operator
try:
    import xlrd
    try:
        from xlrd import xlsx # pylint: disable=W0611
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

_logger = logging.getLogger(__name__)


class WizardSalaryAssingmentsXLS(models.TransientModel):
    _name = "wizard.salary.assingments.xls"

    file_xls = fields.Binary("File XLS/XLSX", required=True)
    without_header = fields.Boolean(
        "Without header",
        help="If is true delete the first line in xls")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('successful', 'Successful'),
        ('error', 'Error'),
    ], default="draft")
    type_amount = fields.Selection([
        ('manual', 'Manual'),
        ('diario', 'Salario diario según contrato'),
        ('hora', 'Salario por hora segun contrato'),
    ], default="manual")
    error_message = fields.Text(readonly=True)

    def validate_length_columns(self, field):
        if not xlrd:
            raise ValueError(
                _("Unable to load xls file: requires Python module xlrd"))
        data = base64.b64decode(self.file_xls)
        book = xlrd.open_workbook(file_contents=data)
        ncols = book.sheet_by_index(0).ncols
        if ncols > len(field):
            message = _(
                "The number of columns indicated in xls is greater than"
                "the columns allowed, the format must be:"
                "Name of the Employee, Name of the Salary Rule,"
                "Date of the Assignment (DD/MM/YYYY),"
                "Payment Date (DD/MM/YYYY), Quantity, Rate (1-100),"
                "Amount, Contract , Salaried Structure")
            raise ValueError(message)
        if ncols < len(field)-2:
            message = _(
                "The number of columns indicated in xls is less than"
                "the columns allowed, the minimum allowed is 7")
            raise ValueError(message)
        if len(field) <= ncols >= len(field)-2:
            field = field[0: ncols]
        return field

    def compose_html_error(self, messages):
        colors = {'error': 'red', 'warning': 'yellow', 'info': 'green'}
        html = ""
        for msg in messages:
            if msg['type'] in ['error', 'warning']:
                self.state = 'error'
            color = colors.get(msg['type'], 'green')
            msg['color'] = color
            html += (
                "<p style=color:{color}>{message}</p><br/>".format(
                    **msg))
        self.error_message = html
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'res_model': 'wizard.salary.assingments.xls',
            'target': 'new',
        }

    def set_amount(self, salary_ids):
        for record in salary_ids:
            if not record.employee_id:
                continue
            contract = record.employee_id.contract_ids.filtered(
                lambda x: x.state == 'open')
            contract = (
                contract and contract[0] or
                record.employee_id.contract_id)
            if self.type_amount == 'diario':
                dayly_salary = (
                    (contract.schedule_pay == 'monthly' and
                        contract.wage_daily_average) or
                    (contract.schedule_pay == 'bi-weekly' and
                        contract.bw_wage_daily_average) or
                    (contract.schedule_pay == 'weekly' and
                        contract.w_wage_daily_average))
                record.amount = dayly_salary
            else:
                hour_salary = (
                    (contract.schedule_pay == 'monthly' and
                        contract.wage_hourly_average) or
                    (contract.schedule_pay == 'bi-weekly' and
                        contract.bw_wage_hourly_average) or
                    (contract.schedule_pay == 'weekly' and
                        contract.w_wage_hourly_average))
                record.amount = hour_salary

    def load_file(self):
        self.ensure_one()
        self._cr.execute('SAVEPOINT import')
        import_fields = [
            'employee_id', 'salary_rule_id', 'date_assing', 'date_paid',
            'quantity', 'rate', 'amount', 'contract_id', 'struct_id'
        ]
        try:
            import_fields = self.validate_length_columns(import_fields)
            data, import_fields = self._convert_import_data(
                import_fields, {'headers': not self.without_header})
            data = self._parse_import_data(data, import_fields)
        except ValueError as error:
            message = [{
                'type': 'error',
                'message': pycompat.text_type(error),
                'record': False}]
            return self.compose_html_error(message)
        model = self.env['hr.salary.assingments'].with_context(
            import_file=True)
        defer_parent_store = self.env.context.get(
            'defer_parent_store_computation', True)
        if defer_parent_store and model._parent_store:
            model = model.with_context(defer_parent_store_computation=True)
        import_result = model.load(import_fields, data)
        if import_result.get('ids', False) and self.type_amount != 'manual':
            salary_ids = self.env['hr.salary.assingments'].browse(
                import_result.get('ids'))
            self.set_amount(salary_ids)
        _logger.info('done')
        try:
            self._cr.execute('RELEASE SAVEPOINT import')
        except psycopg2.InternalError:
            pass
        for mss in import_result.get('messages', False):
            if mss.get('message')[0:43] == \
                    "Found multiple matches for field 'Contract'":
                import_result.get('messages', False).remove(mss)
        if not import_result['messages']:
            return {'type': 'ir.actions.client', 'tag': 'reload'}
        return self.compose_html_error(import_result['messages'])

    @api.model
    def _convert_import_data(self, fields_val, options):
        """ Extracts the input BaseModel and fields list (with
            ``False``-y placeholders for fields to *not* import) into a
            format Model.import_data can use: a fields list without holes
            and the precisely matching data matrix
            :param list(str|bool): fields
            :returns: (data, fields)
            :rtype: (list(list(str)), list(str))
            :raises ValueError: in case the import data could not be converted
        """
        indices = [index for index, field in enumerate(fields_val) if field]
        if not indices:
            raise ValueError(_(
                "You must configure at least one field to import"))
        if len(indices) == 1:
            mapper = lambda row: [row[indices[0]]]
        else:
            mapper = operator.itemgetter(*indices)
        import_fields = [f for f in fields_val if f]
        rows_to_import = self._read_xls()
        if options.get('headers'):
            rows_to_import = itertools.islice(rows_to_import, 1, None)
        data = [
            list(row) for row in pycompat.imap(mapper, rows_to_import)
            if any(row)
        ]
        return data, import_fields

    def _parse_import_data(self, data, fields_val):
        base_import = self.env['base_import.import']
        return base_import._parse_import_data_recursive(
            'hr.salary.assingments', '', data, fields_val, {})

    def _read_xls(self):
        """ Read file content, using xlrd lib """
        base_import = self.env['base_import.import']
        data = base64.b64decode(self.file_xls)
        book = xlrd.open_workbook(file_contents=data)
        return base_import._read_xls_book(book)
