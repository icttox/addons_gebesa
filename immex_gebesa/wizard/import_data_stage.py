# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import zipfile
import tempfile
import io
import os
from odoo import _, fields, api, models
from odoo.exceptions import ValidationError

MODELS_IMPORT = {
    # '_501.asc': 'l10n.mx.immex.pedimento',
    '_502.asc': 'l10n.mx.immex.pedimento.transporte',
    '_503.asc': 'l10n.mx.immex.pedimento.guia',
    '_504.asc': 'l10n.mx.immex.pedimento.contenedor',
    '_505.asc': 'l10n.mx.immex.pedimento.factura',
    '_506.asc': 'l10n.mx.immex.pedimento.fechas',
    '_507.asc': 'l10n.mx.immex.pedimento.casos',
    '_508.asc': 'l10n.mx.immex.pedimento.cuentas',
    '_509.asc': 'l10n.mx.immex.pedimento.tasas',
    '_510.asc': 'l10n.mx.immex.pedimento.contribuciones',
    '_511.asc': 'l10n.mx.immex.pedimento.observaciones',
    '_512.asc': 'l10n.mx.immex.pedimento.descargos',
    '_520.asc': 'l10n.mx.immex.pedimento.destinatarios',
    # '_551.asc': 'l10n.mx.immex.partida',
    '_552.asc': 'l10n.mx.immex.mercancias',
    '_553.asc': 'l10n.mx.immex.partida.permisos',
    '_554.asc': 'l10n.mx.immex.partida.casos',
    '_555.asc': 'l10n.mx.immex.partida.garantias',
    '_556.asc': 'l10n.mx.immex.partida.tasas',
    '_557.asc': 'l10n.mx.immex.partida.contribuciones',
    '_558.asc': 'l10n.mx.immex.partida.observaciones',
    '_701.asc': 'l10n.mx.immex.pedimento.rectificaciones',
    '_702.asc': 'l10n.mx.immex.pedimento.diferencias',
    '_Inci.asc': 'l10n.mx.immex.incidencias.reconocimiento',
    '_Sel.asc': 'l10n.mx.immex.pedimento.seleccion'
}


class ImportDataStage(models.TransientModel):
    _name = 'import.data.stage'
    _description = 'descripcion pendiente'

    zip_file = fields.Binary(
        string='File Zip',
        filters='*.zip',
        required=True)

    @api.multi
    def import_data_stage_wz_m(self):
        tmp = tempfile.mkdtemp()
        with zipfile.ZipFile(io.BytesIO(
                base64.decodebytes(self.zip_file))) as zip_file:
            zip_file.extractall(tmp)
        resumen = False

        for file in os.listdir(tmp):
            if os.path.isfile(os.path.join(tmp, file)) and '_Resumen.asc' in file:
                with open(os.path.join(
                        tmp, file), errors='replace') as file_asc:

                    resumen = self.env['l10n.mx.immex.resumen'].import_for_data_stage(
                        file_asc.readlines()[1:])

                    self.env['ir.attachment'].create({
                        'name': resumen.folio,
                        'datas': self.zip_file,
                        'datas_fname': resumen.folio + '.zip',
                        'res_model': 'l10n.mx.immex.resumen',
                        'res_id': resumen.id,
                        'type': 'binary',
                    })

        if not resumen:
            raise ValidationError(_("The summary file was not found"))

        for file in os.listdir(tmp):
            if os.path.isfile(os.path.join(tmp, file)) and '_501.asc' in file:
                with open(os.path.join(
                        tmp, file), errors='replace') as file_asc:
                    self.env['l10n.mx.immex.pedimento'].import_for_data_stage(
                        file_asc.readlines()[1:], resumen)

        for file in os.listdir(tmp):
            if os.path.isfile(os.path.join(tmp, file)) and '_551.asc' in file:
                with open(os.path.join(
                        tmp, file), errors='replace') as file_asc:
                    self.env['l10n.mx.immex.partida'].import_for_data_stage(
                        file_asc.readlines()[1:], resumen)

        for file in os.listdir(tmp):
            if not os.path.isfile(os.path.join(tmp, file)):
                continue
            with open(os.path.join(tmp, file), errors='replace') as file_asc:
                name_file = '_' + file.split('_')[1]

                if name_file in MODELS_IMPORT:
                    self.env[MODELS_IMPORT[name_file]].import_for_data_stage(
                        file_asc.readlines()[1:], resumen)
