# Copyright 2021, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models
import pytz


class Order(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "jinja.mixin"]

    def view_data(self):
        tz = pytz.timezone(self._context.get('tz') or 'UTC')
        return {
            "env": self.env,
            "message": "Hello, word!",
            "orale": "Ya son las " + fields.datetime.now(tz).strftime(
                '%H:%M:%S')
        }
