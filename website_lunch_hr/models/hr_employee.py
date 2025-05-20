# Copyright 2022, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import base64
import os
from random import choice

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from odoo import api, fields, models
from odoo.exceptions import ValidationError

PARAM_PASS = "lunch_passkey"
PARAM_SALT = "lunch_salt"


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def create_lunch_employee(self):
        self.ensure_one()

        product = self.env.ref('website_lunch_hr.producto_platillo')
        if not product:
            raise ValidationError("No se encontro un producto para la comida")

        values_order = {
            'user_id': self.env.user.id,
            'employee_id': self.id,
            'state': 'confirmed',
            'order_line_ids': [],
        }
        order_id = self.env['lunch.order'].sudo().create(values_order)

        values = {
            'product_id': product.id,
            'state': 'confirmed',
            'note': 'Creado desde website',
            'order_id': order_id.id,
        }
        order_line_id = self.env['lunch.order.line'].sudo().create(values)

        return self.env.ref(
            'website_lunch_hr.action_lunch_ticket').report_action(order_line_id)

    def get_random_password(self):
        for employee in self:
            employee.lunch_pass = self.get_random_string()

    def get_urlsafe_key(self):

        config_param = self.env["ir.config_parameter"]
        salt = None
        passphrase = config_param.sudo().get_param(PARAM_PASS)
        if not passphrase:
            passphrase = base64.urlsafe_b64encode(os.urandom(64)).decode()
            salt = os.urandom(16)
            config_param.sudo().set_param(PARAM_PASS, passphrase)
            config_param.sudo().set_param(
                PARAM_SALT, base64.urlsafe_b64encode(salt).decode()
            )
        else:
            salt = base64.urlsafe_b64decode(
                config_param.sudo().get_param(PARAM_SALT).encode()
            )

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256,
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

    @api.model
    def encrypt_string(self, plaintext):
        """Returns a URL-safe string containing the encrypted version of plaintext."""

        key = self.get_urlsafe_key()
        f = Fernet(key)
        cipher = f.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(cipher)

    @api.model
    def decrypt_password_as_string(self, obj_id):
        """Returns a string representing the plaintext password in record with
        database ID obj_id."""

        key = self.get_urlsafe_key()
        f = Fernet(key)

        plaintext = False
        rec = self.browse(obj_id)
        token = base64.urlsafe_b64decode(rec.lunch_pass)
        plaintext = f.decrypt(token).decode()
        return plaintext

    lunch_pass = fields.Char()

    @api.model
    def get_random_string(self):
        longitud = 4
        valores = (
            "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )
        p = ""
        p = p.join([choice(valores) for i in range(longitud)])
        return p

    def write(self, vals):

        # Encrypt the password before saving it. The unencrypted password should not be
        # saved to the database even temporarily.
        #
        if "lunch_pass" in vals.keys() and vals["lunch_pass"] is not False:
            vals["lunch_pass"] = self.encrypt_string(vals["lunch_pass"])

        # if "active" in vals.keys() and vals["active"] is False:
        #     vals["user_inactive_id"] = self.env.user.id
        #     vals["inactivation_date"] = fields.Datetime.now()
        return super(HrEmployee, self).write(vals)

    @api.model
    def create(self, vals):

        # Encrypt the password before saving it. The unencrypted password should not be
        # saved to the database even temporarily.
        #
        if "lunch_pass" in vals.keys() and vals["lunch_pass"] is not False:
            vals["lunch_pass"] = self.encrypt_string(vals["lunch_pass"])

        res = super(HrEmployee, self).create(vals)

        return res
