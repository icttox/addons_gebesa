# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)


from odoo import models, fields, api


class allinoneMessage(models.TransientModel):
    _name = "allinone.message"
    _description = "Warn"

    @api.model
    def default_get(self, fields):
        res = {}
        if self._context and self._context.get('action', 'purchase'):
            res.update({'message': 'Are you sure you want to generate '+ self._context["action"]+' Entries?'})
        return res

    message = fields.Text('Text', readonly=True)

    @api.multi
    def action_validate(self):
        """
        -Perform action
            -Purchase,
            -Sales,
            -Transfers,
            -Reco
        """
        records = self.env['allinone.import'].browse(self._context.get('active_ids',[]))
        records.action_validate()
