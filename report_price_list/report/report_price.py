# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import UserError


class ParticularReport(models.AbstractModel):
    _name = 'report.report_price_list.report_price_list'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'product.line'
        lines = self.env[self.model].browse(docids)
#         line_obj = self.env['product.line']
        product_obj = self.env['product.template']
        gpo_obj = self.env['product.group']
        line_obj = self.env['product.line']
        groups = []
        tipos = []
        products = []
        claves_p = []
        categorias = []
        claves_categoria = []
        mod_tp = []
#         nombres = ''
        for line in lines:
            if line.report_type == 'normal':
                product_tmplt = product_obj.search([
                    ('pricelist', '=', True),
                    ('is_line', '=', True),
                    ('line_id', '=', line.id)],
                    order=None
                )
                if product_tmplt:
                    categoria = product_tmplt.mapped('pricelist_categ_id')
                    for cat in categoria:
                        categorias.append(cat)
                        claves_cat = product_tmplt.filtered(lambda x: x.pricelist_categ_id == cat)
                        for cc in claves_cat:
                            claves_categoria.append(cc)
                    tipos_p = product_tmplt.mapped('type_id')
                    for tp in tipos_p:
                        tipos.append(tp)
                    # claves = product_tmplt.filtered(lambda x: x.type_id.ids == tp.ids)
                    # for clv in claves:
                    #     if clv:
                    #         cl = product_tmplt.reference_mask + ', '
                    #         claves_p.append(cl)
                    # if product_tmplt.group_id.name and product_tmplt.type_id.name:
                    # claves = product_tmplt.reference_mask + ', '
                    gp = product_tmplt.mapped('group_id')
                    for g in gp:
                        groups.append(g)
                    # productos = gpo_obj.search([
                    #     ('name', '=', product_tmplt.name)],
                    # )

                    for product in product_tmplt:
                        # gp = product.mapped('group_id')
                        # groups.append(gp)
                        products.append(product)
                if not product_tmplt:
                    raise UserError(_("There is no price list."))
            if line.report_type == 'modulares':
                lin = line_obj.search([('name', '=', 'Synergy'),
                                       ('code', '=', 'GES')])
                group = gpo_obj.search([('name', '=', 'Mamparas')])
                product = product_obj.search([('group_id', '=', group.id),
                                                ('line_id', '=', lin.id),
                                                ('name', 'not like',
                                                "% Mixta %"),
                                                ('is_line', '=', True)],
                                                order="height, length")
                tipos_mod = product.mapped('type_id')
                for tm in tipos_mod:
                    mod_tp.append(tm)
#                     claves += product.reference_mask + ', '
#                     nombres += product.name + ', '
#                     line_id = product.line_id
#                     group_id = product.group_id
#                     if line_id not in docs:
#                         docs.append(line_id)
#                         groups[line_id.id] = []
#                     if group_id not in groups[line_id.id]:
#                         groups[line_id.id].append(group_id)
#                         products[str(line_id.id) + '-' + str(group_id.id)] = []
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': lines,
            'products': products,
            'groups': groups,
            'tipos': tipos,
            'claves_p': claves_p,
            'categorias': categorias,
            'claves_categoria': claves_categoria,
            'mod_tp': mod_tp,
        }
        return docargs
