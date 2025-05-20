from odoo import api, fields, models
from odoo.exceptions import ValidationError
import io
import base64


class TxtReportWizard(models.TransientModel):
    _name = 'txt.report.wizard'
    _description = 'TXT Report Wizard'

    name = fields.Char(string='File Name', required=True)
    data = fields.Binary(string='File', readonly=True)
    extra_time = fields.Boolean(string='Extra Time',)

    @api.multi
    def generate_report(self):
        if self.extra_time:
            return self.generate_report_extra_time()
        else:
            # import ipdb; ipdb.set_trace()
            # Replace 'model_name' with the name of the model you want to report on
            model_obj = self.env['hr.salary.assingments']
            # Replace 'field_1' and 'field_2' with the fields you want to include in the report
            active_ids = self._context.get('active_ids', []) or []
            report_data = model_obj.browse(active_ids)
            report = io.StringIO()
            for data in report_data:
                if not data['employee_id'][0]['identification_id']:
                    raise ValidationError('El empleado %s no tiene un numero de identificacion' % data.employee_id.name)
                report.write("|1|{}\n".format(data['employee_id'][0]['identification_id'].lstrip('0') + ',S,C'))
                report.write("|1.1|{}\n".format(data['salary_rule_id'][0]['code'] + ',' + '{:,.2f}'.format(data['amount']) + ',0.00'))
            report.seek(0)
            file_data = report.read().encode('utf-8')
            file_name = self.name + ".txt"
            self.write({'data': base64.encodestring(file_data), 'name': file_name})
            return {
                'name': 'TXT Report',
                'type': 'ir.actions.act_url',
                'url': '/web/content/?model=txt.report.wizard&id={}&field=data&download=true&filename={}'.format(self.id, file_name),
                'target': 'self'
            }

    def generate_report_extra_time(self):
        # Replace 'model_name' with the name of the model you want to report on
        model_obj = self.env['hr.salary.assingments']
        # Replace 'field_1' and 'field_2' with the fields you want to include in the report
        active_ids = self._context.get('active_ids', []) or []
        report_data = model_obj.browse(active_ids)
        report = io.StringIO()
        for data in report_data:
            if not data['employee_id'][0]['identification_id']:
                raise ValidationError('El empleado %s no tiene un numero de identificacion' % data.employee_id.name)
            days = str(data.days).zfill(2)
            report.write("|1|{}\n".format(data['employee_id'][0]['identification_id'].lstrip('0') + ',' + '{:04d}'.format(int(data['quantity'] * 100)) + ',' + days + ',S,C'))
        report.seek(0)
        file_data = report.read().encode('utf-8')
        file_name = self.name + ".txt"
        self.write({'data': base64.encodestring(file_data), 'name': file_name})
        return {
            'name': 'TXT Report',
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=txt.report.wizard&id={}&field=data&download=true&filename={}'.format(self.id, file_name),
            'target': 'self'
        }
