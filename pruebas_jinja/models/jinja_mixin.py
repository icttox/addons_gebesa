# Copyright 2021, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models
from jinja2 import Environment


class JinjaMixin(models.AbstractModel):
    """Model mixin to enable jinja templating"""
    _name = "jinja.mixin"

    templater = Environment(
        variable_start_string="{{{",
        variable_end_string="}}}",
    )

    def view_data(self):
        return {}

    def fields_view_get(self, *args, **kwargs):
        res = super().fields_view_get(*args, **kwargs)
        res["arch"] = self.templater.from_string(res["arch"]).render(
            **self.view_data())
        return res
