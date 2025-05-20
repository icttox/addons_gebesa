from odoo import http

import os
import jinja2
import json

path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
loader = jinja2.FileSystemLoader(path)

env = jinja2.Environment(loader=loader, autoescape=True)
env.filters["json"] = json.dumps

class ProductionFloor(http.Controller):

    @http.route('/production_floor/', auth='public')
    def index(self, **kw):
        return env.get_template("index.html").render()
