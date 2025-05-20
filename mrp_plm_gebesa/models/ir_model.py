# -*- coding: utf-8 -*-
# © 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2016 ACSONE SA/NA (<http://acsone.eu>)

from odoo import models


class IrModel(models.Model):
    _inherit = 'ir.model'

    # def _patch_quick_create(self, cr, ids):

    #     def _wrap_name_create():
    #         def wrapper(self, cr, uid, name, context=None):
    #             raise UserError(_("Can't create quickly. Opening create form"))
    #         return wrapper

    #     for model in self.browse(cr, SUPERUSER_ID, ids):
    #         if model.avoid_quick_create:
    #             model_name = model.model
    #             model_obj = self.pool.get(model_name)
    #             if model_obj and not hasattr(model_obj, 'check_quick_create'):
    #                 if not str(model_obj) == 'res.partner' or str(model_obj) == 'project.task': # or str(model_obj) == 'account.account':
    #                     model_obj._patch_method('name_create', _wrap_name_create())
    #                     model_obj.check_quick_create = True
    #     return True
