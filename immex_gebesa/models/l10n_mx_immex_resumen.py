# -*- coding: utf-8 -*-
# © <2021> <Samuel Barron, GEBESA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models
from odoo.exceptions import ValidationError


class L10nMxImmexResumen(models.Model):
    _name = 'l10n.mx.immex.resumen'
    _inherit = ['message.post.show.all']
    _rec_name = 'folio'

    folio = fields.Char(
        string='Folio',
    )
    rfc = fields.Char(
        string='RFC',
    )
    fechaini = fields.Datetime(
        string='Fecha inicio',
    )
    fechafin = fields.Datetime(
        string='Fecha final',
    )
    fechaexe = fields.Char(
        string='Fecha de ejecucion',
    )
    pedimento_ids = fields.One2many(
        'l10n.mx.immex.pedimento',
        'resumen_id',
        string='Pedimento'
    )

    def import_for_data_stage(self, lines):
        for line in lines:
            line = line.replace('\r\n', '')
            line = line.replace('\x00', '')
            line = line.split("|")

            self._cr.execute("""
                SELECT
                    folio,
                    fechaini,
                    fechafin
                FROM l10n_mx_immex_resumen
                WHERE %s BETWEEN fechaini AND fechafin
                    OR %s BETWEEN fechaini AND fechafin
                limit 1""", (line[2], line[3]))

            if self._cr.rowcount:
                error_date = self._cr.fetchone()
                raise ValidationError(
                    "Las fechas de este archivo se traslapan \
                    con las del folio %s: %s al %s" % (
                        error_date[0], error_date[1], error_date[2]
                    ))

            resumen = self.create({
                'folio': line[0],
                'rfc': line[1],
                'fechaini': line[2],
                'fechafin': line[3],
                'fechaexe': line[4],
            })

        return resumen
