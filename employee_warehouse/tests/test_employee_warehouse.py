# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestHrEmployee(TransactionCase):

    # Variables Globales
    def setUp(self):
        super(TestHrEmployee, self).setUp()
        self.employee = self.env['hr.employee']
        self.warehouse = self.env.ref('stock.warehouse0')

    # Metodos globales
    def create_employee(self, name, default_warehouse):
        self.employee.create({
            'name': name,
            'default_warehouse_id': default_warehouse
        })

    # Metodos de Test
    def test_10_employee_default_warehouse_not_in_warehouses(self):
        with self.assertRaisesRegexp(
                ValidationError,
                "The default warehouse must be selected in the \
                      warehouse of employee"):
            self.create_employee('empleado1', self.warehouse.id)
