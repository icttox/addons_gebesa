
from json.decoder import JSONDecodeError
from odoo import models, api
from odoo.exceptions import UserError
import requests


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def read_deal(self):
        if not self.hubspot_id:
            return
        url = "https://api.hubapi.com/crm/v3/objects/deals/" + self.hubspot_id
        querystring = {
            "paginateAssociations": "false",
            "archived": "false",
            "hapikey": self.env.user.company_id.apikey}
        headers = {'accept': 'application/json'}
        try:
            response = requests.request(
                "GET", url, headers=headers, params=querystring)
        except requests.exceptions.RequestException as req_e:
            return {'status': 'error', 'message': str(req_e)}
        except requests.exceptions.HTTPError as res_e:
            msg = str(res_e)
        except JSONDecodeError:
            return {'status': 'error', 'message': msg}
        if response.text == '':
            raise UserError("Deal no existe")
        raise UserError(response.text)
        # print(response.text)

    @api.multi
    def read_deal_json(self):
        url = "https://api.hubapi.com/crm/v3/objects/deals/search"
        querystring = {"hapikey": self.env.user.company_id.apikey}
        payload = "{\"filterGroups\":[],\"sorts\":[]}"
        headers = {
            'accept': "application/json",
            'content-type': "application/json"}
        response = requests.request(
            "POST", url, data=payload, headers=headers, params=querystring)
        # print(response.text)
        raise UserError(response.text)
