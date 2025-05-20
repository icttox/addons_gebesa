# -*- coding: utf-8 -*-
# © <2021> <Samuel Barron, GEBESA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class L10nMxImmexPedimentoGuia(models.Model):
    _name = 'l10n.mx.immex.pedimento.documentos.digitalizados'
    _description = 'descripcion pendiente'

    name = fields.Char(
        string='Nombre',
    )
    pedimento_id = fields.Many2one(
        'l10n.mx.immex.pedimento',
        string='Pedimento',
    )
