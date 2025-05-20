# Copyright 2024, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.http import request, route
from odoo.addons.base.controllers.rpc import RPC


class CustomRPC(RPC):

    @route('/jsonrpc', type='json', auth="none", save_session=False)
    def jsonrpc(self, service, method, args):
        if method in ('execute_kw'):
            # import ipdb; ipdb.set_trace()
            method_args = args[5]
            count_arg = 0
            for m_arg in method_args:
                if isinstance(m_arg, dict):
                    if 'res_id' in m_arg and 'res_model' in m_arg:
                        rec = request.env[m_arg['res_model']].browse(
                            m_arg['res_id'])
                        method_args[count_arg] = rec
                count_arg += 1
        return super().jsonrpc(service, method, args)
