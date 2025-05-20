# -*- coding: utf-8 -*-

from odoo import models, fields


class HrEmployeeMedicalExpenseLine(models.Model):
    _name = "hr.employee.medical.expense.line"
    _description = "Employee Medical Expense Line"

    medicalexp_id = fields.Many2one(
        'hr.employee.medical.expense',
        string="Employee Medical Expense",
    )

    product_sat_code_id = fields.Many2one(
        'l10n_mx_edi.product.sat.code',
        string="Product SAT Code",
    )

    description = fields.Char(
        string='Description',
        size=250,
        required=True)

    unit = fields.Char(
        string='Unit',
        size=250,
        required=True)

    quantity = fields.Float(
        string='Quantity',
    )

    price_unit = fields.Float(
        string='Price Unit',
    )

    total = fields.Float(
        string='Total',
    )

    authorized = fields.Boolean(
        string='Authorized',
    )

    refund = fields.Boolean(
        string='Refund',
    )
