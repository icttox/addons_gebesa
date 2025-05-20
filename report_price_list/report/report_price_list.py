# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class ParticularReport(models.AbstractModel):
    _name = 'report.report_price_list.report_price_list_isometric'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'product.line'
        #report_obj = self.env['report']
        line_obj = self.env['product.line']
        group_obj = self.env['product.group']
        product_obj = self.env['product.template']

        #report = report_obj._get_report_from_name(
        #    'report_price_list.report_price_list_isometric')
        lines = line_obj.browse(docids)
        order_key = []
        order_key_len = []
        titles = {}

        for line in lines:
            if line.report_type == 'normal':
                product_tamplate = product_obj.search([
                    ('pricelist', '=', True),
                    ('is_line', '=', True),
                    ('line_id', '=', line.id)],
                    order=None
                )
                if product_tamplate:
                    titles[line.name] = {}
                    titles[line.name]['line'] = line
                    titles[line.name]['page'] = []
                    page = []
                    count = 0
                    for product in product_tamplate:
                        if count == 5:
                            titles[line.name]['page'].append(page)

                            page = []
                            count = 0
                        page.append(product)
                        count += 1
                    if page:
                        titles[line.name]['page'].append(page)
                if not product_tamplate:
                    raise UserError(_("There is no price list."))
            elif line.report_type == 'modulares':
                titles['MODULARE'] = {}
                titles['MODULARE']['line'] = line
                titles['MODULARE']['page'] = {}
                titles['MODULARE']['page'][1] = {}
                lin = line_obj.search([('name', '=', 'Synergy'),
                                       ('code', '=', 'GES')])
                group = group_obj.search([('name', '=', 'Mamparas')])
                product = product_obj.search([('group_id', '=', group.id),
                                              ('line_id', '=', lin.id),
                                              ('name', 'not like',
                                               "% Mixta %"),
                                              ('is_line', '=', True)],
                                             order="height, length")
                for prod in product:
                    if prod.height in titles['MODULARE']['page'][1].keys():
                        titles['MODULARE']['page'][1][
                            prod.height].append(prod)
                    else:
                        order_key.append(prod.height)
                        titles['MODULARE']['page'][1][prod.height] = []
                        titles['MODULARE']['page'][1][
                            prod.height].append(prod)

                titles['MODULARE']['page'][2] = {}
                group = group_obj.search([('name', '=', 'Postes')])
                product = product_obj.search([('group_id', '=', group.id),
                                              ('line_id', '=', lin.id),
                                              ('is_line', '=', True)],
                                             order="height")
                titles['MODULARE']['page'][2]['postes'] = []
                for prod in product:
                    titles['MODULARE']['page'][2]['postes'].append(prod)
                group = group_obj.search([('name', '=', 'Remates')])
                product = product_obj.search([('group_id', '=', group.id),
                                              ('line_id', '=', lin.id),
                                              ('is_line', '=', True)],
                                             order="height")
                titles['MODULARE']['page'][2]['Tapa1'] = []
                titles['MODULARE']['page'][2]['Tapa2'] = []
                for prod in product:
                    if 'Remate' in str(prod.name):
                        titles['MODULARE']['page'][2]['Tapa1'].append(prod)
                    else:
                        titles['MODULARE']['page'][2]['Tapa2'].append(prod)

                titles['MODULARE']['page'][3] = {}
                titles['MODULARE']['page'][4] = {}
                titles['MODULARE']['page'][4]['Inf'] = {}
                titles['MODULARE']['page'][4]['Sup'] = {}
                titles['MODULARE']['page'][5] = {}
                titles['MODULARE']['page'][5]['Sup'] = {}
                lin = line_obj.search([('name', '=', 'Optimus'),
                                       ('code', '=', 'GEO')])
                group = group_obj.search([('name', '=', 'Mamparas')])
                product = product_obj.search([('group_id', '=', group.id),
                                              ('line_id', '=', lin.id),
                                              ('is_line', '=', True)],
                                             order="height, length")
                for prod in product:
                    if 'Estructura' in str(prod.name):
                        if prod.height in titles['MODULARE']['page'][3].keys():
                            titles['MODULARE']['page'][3][prod.height].append(
                                prod)
                        else:
                            titles['MODULARE']['page'][3][prod.height] = []
                            titles['MODULARE']['page'][3][prod.height].append(
                                prod)
                    else:
                        if 'CN' in str(prod.name):
                            key = 'CN'
                        if 'BP' in str(prod.name):
                            key = 'BP'
                        if 'Tapiz' in str(prod.name):
                            key = 'Tapiz'
                        if 'Pintarron' in str(prod.name):
                            key = 'Pintarron'
                        if 'Inf' in str(prod.name):
                            if prod.length not in titles['MODULARE']['page'][
                                    4]['Inf'].keys():
                                order_key_len.append(prod.length)
                                titles['MODULARE']['page'][4]['Inf'][
                                    prod.length] = {}
                            titles['MODULARE']['page'][4]['Inf'][prod.length][
                                key] = prod
                        if 'Sup' in str(prod.name):
                            if 3 >= len(titles['MODULARE']['page'][4][
                                    'Sup'].keys() + titles['MODULARE']['page'][
                                    5]['Sup'].keys()):
                                if prod.height not in titles['MODULARE'][
                                        'page'][4]['Sup'].keys():
                                    if 3 == len(titles['MODULARE']['page'][4][
                                            'Sup'].keys()):
                                        titles['MODULARE']['page'][5]['Sup'][
                                            prod.height] = {}
                                        titles['MODULARE']['page'][5]['Sup'][
                                            prod.height][
                                            prod.length] = {}
                                        titles['MODULARE']['page'][5]['Sup'][
                                            prod.height][prod.length][
                                            key] = prod
                                        continue
                                    else:
                                        titles['MODULARE']['page'][4]['Sup'][
                                            prod.height] = {}
                                if prod.length not in titles['MODULARE'][
                                        'page'][4]['Sup'][prod.height].keys():
                                    titles['MODULARE']['page'][4]['Sup'][
                                        prod.height][prod.length] = {}
                                titles['MODULARE']['page'][4]['Sup'][
                                    prod.height][prod.length][key] = prod
                            else:
                                if prod.height not in titles['MODULARE'][
                                        'page'][5]['Sup'].keys():
                                    titles['MODULARE']['page'][5]['Sup'][
                                        prod.height] = {}
                                if prod.length not in titles['MODULARE'][
                                        'page'][5]['Sup'][prod.height].keys():
                                    titles['MODULARE']['page'][5]['Sup'][
                                        prod.height][prod.length] = {}
                                titles['MODULARE']['page'][5]['Sup'][
                                    prod.height][prod.length][key] = prod
                titles['MODULARE']['page'][6] = {}
                group = group_obj.search([('name', '=', 'Postes')])
                product = product_obj.search([('group_id', '=', group.id),
                                              ('line_id', '=', lin.id),
                                              ('is_line', '=', True)],
                                             order="height, vias")
                titles['MODULARE']['page'][6]['postes'] = {}
                for prod in product:
                    if prod.height not in titles['MODULARE']['page'][6][
                            'postes'].keys():
                        titles['MODULARE']['page'][6]['postes'][
                            prod.height] = {}
                    titles['MODULARE']['page'][6]['postes'][prod.height][
                        prod.vias] = prod
                group = group_obj.search([('name', '=', 'Remates')])
                product = product_obj.search([('group_id', '=', group.id),
                                              ('line_id', '=', lin.id),
                                              ('is_line', '=', True)],
                                             order="height")
                titles['MODULARE']['page'][6]['Tapa1'] = []
                titles['MODULARE']['page'][6]['Tapa2'] = []
                for prod in product:
                    if 'Remate' in str(prod.name):
                        titles['MODULARE']['page'][6]['Tapa1'].append(prod)
                    else:
                        titles['MODULARE']['page'][6]['Tapa2'].append(prod)
                titles['MODULARE']['page'][7] = {}
                titles['MODULARE']['page'][8] = {}
                lin = line_obj.search([('name', '=', 'Ellite'),
                                       ('code', '=', 'GEL')])
                group = group_obj.search([('name', '=', 'Mamparas')])
                product = product_obj.search([('group_id', '=', group.id),
                                              ('line_id', '=', lin.id),
                                              ('is_line', '=', True)],
                                             order="height, length")
                for prod in product:
                    if prod.height not in order_key:
                        order_key.append(prod.height)
                    if 'Estructura' in str(prod.name):
                        if prod.height in titles['MODULARE']['page'][7].keys():
                            titles['MODULARE']['page'][7][prod.height].append(
                                prod)
                        else:
                            titles['MODULARE']['page'][7][prod.height] = []
                            titles['MODULARE']['page'][7][prod.height].append(
                                prod)
                    elif 'Ta/Pi'in str(prod.name):
                        if prod.height not in titles['MODULARE']['page'][
                                8].keys():
                            titles['MODULARE']['page'][8][prod.height] = {}
                        if prod.length not in titles['MODULARE']['page'][8][
                                prod.height].keys():
                            titles['MODULARE']['page'][8][prod.height][
                                prod.length] = {}
                        titles['MODULARE']['page'][8][prod.height][
                            prod.length][3] = prod
                    elif 'Tapiz'in str(prod.name):
                        if prod.height not in titles['MODULARE']['page'][
                                8].keys():
                            titles['MODULARE']['page'][8][prod.height] = {}
                        if prod.length not in titles['MODULARE']['page'][8][
                                prod.height].keys():
                            titles['MODULARE']['page'][8][prod.height][
                                prod.length] = {}
                        titles['MODULARE']['page'][8][prod.height][
                            prod.length][2] = prod
                    elif 'Acrilico'in str(prod.name):
                        if prod.height not in titles['MODULARE']['page'][
                                8].keys():
                            titles['MODULARE']['page'][8][prod.height] = {}
                        if prod.length not in titles['MODULARE']['page'][8][
                                prod.height].keys():
                            titles['MODULARE']['page'][8][prod.height][
                                prod.length] = {}
                        titles['MODULARE']['page'][8][prod.height][
                            prod.length][4] = prod
                    elif 'Metalico/Mag'in str(prod.name):
                        if prod.height not in titles['MODULARE']['page'][
                                8].keys():
                            titles['MODULARE']['page'][8][prod.height] = {}
                        if prod.length not in titles['MODULARE']['page'][8][
                                prod.height].keys():
                            titles['MODULARE']['page'][8][prod.height][
                                prod.length] = {}
                        titles['MODULARE']['page'][8][prod.height][
                            prod.length][1] = prod
                    elif 'CN'in str(prod.name):
                        if prod.height not in titles['MODULARE']['page'][
                                8].keys():
                            titles['MODULARE']['page'][8][prod.height] = {}
                        if prod.length not in titles['MODULARE']['page'][8][
                                prod.height].keys():
                            titles['MODULARE']['page'][8][prod.height][
                                prod.length] = {}
                        titles['MODULARE']['page'][8][prod.height][
                            prod.length][7] = prod
                    elif 'BP'in str(prod.name):
                        if prod.height not in titles['MODULARE']['page'][
                                8].keys():
                            titles['MODULARE']['page'][8][prod.height] = {}
                        if prod.length not in titles['MODULARE']['page'][8][
                                prod.height].keys():
                            titles['MODULARE']['page'][8][prod.height][
                                prod.length] = {}
                        titles['MODULARE']['page'][8][prod.height][
                            prod.length][5] = prod
                    elif 'AP'in str(prod.name):
                        if prod.height not in titles['MODULARE']['page'][
                                8].keys():
                            titles['MODULARE']['page'][8][prod.height] = {}
                        if prod.length not in titles['MODULARE']['page'][8][
                                prod.height].keys():
                            titles['MODULARE']['page'][8][prod.height][
                                prod.length] = {}
                        titles['MODULARE']['page'][8][prod.height][
                            prod.length][6] = prod

                titles['MODULARE']['page'][10] = {}
                group = group_obj.search([('name', '=', 'Postes')])
                product = product_obj.search([('group_id', '=', group.id),
                                              ('line_id', '=', lin.id),
                                              ('is_line', '=', True)],
                                             order="height, vias")
                titles['MODULARE']['page'][10]['postes'] = {}
                for prod in product:
                    if prod.height not in titles['MODULARE']['page'][10][
                            'postes'].keys():
                        titles['MODULARE']['page'][10]['postes'][
                            prod.height] = {}
                    titles['MODULARE']['page'][10]['postes'][prod.height][
                        prod.vias] = prod

        order_key = sorted(order_key)
        order_key_len = sorted(order_key_len)

        docargs = {
            'doc_ids': docids,
            #'doc_model': report.model,
            'doc_model': self.model,
            'docs': titles,
            'order_key': order_key,
            'order_key_len': order_key_len,
        }

        #return report_obj.render(
        #    'report_price_list.report_price_list_isometric',
        #    docargs
        #)
        return docargs
