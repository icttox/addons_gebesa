
from odoo import models, api
from odoo.exceptions import UserError
import requests


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.multi
    def call_hubspot_api(self):
        url = "https://api.hubapi.com/crm/v3/objects/contacts"

        querystring = {"limit":"10","paginateAssociations":"false","archived":"false","hapikey":self.env.user.company_id.apikey}
        headers = {'accept': 'application/json'}
        response = requests.request(
            "GET",
            url,
            headers=headers,
            params=querystring
        )

        raise UserError(response.text)
        # print(response.text)
