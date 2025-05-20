# Copyright 2022, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, api
from odoo.exceptions import ValidationError
from .fiel import Fiel
from .autenticacion import Autenticacion
from .solicitadescarga import SolicitaDescarga
from .verificasolicituddescarga import VerificaSolicitudDescarga
from .descargamasiva import DescargaMasiva
import base64
import logging
from datetime import datetime
import time

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def validar_fiel(self, args):
        try:
            company = self.env['res.company'].search([
                ('id', 'in', args['id'])], limit=1)
            fiel = self.env['cfdi.fiel'].search([
                ('company_id', '=', company.id),
                ('active', '=', True)], order='id',
                limit=1)
            # import ipdb; ipdb.set_trsace()
            fiel = Fiel(base64.decodebytes(
                fiel.fiel_file),
                base64.decodebytes(fiel.fiel_key_file),
                fiel.fiel_password)
            auth = Autenticacion(fiel)
            auth.obtener_token()
            return True
        except Exception:
            raise ValidationError("No se ha podido validar error 500.")

    @api.model
    def descargamasiva(self, args):
        if args['start'].strip() and args['end'].strip():
            _logger.error("Error: SOLICITUD::  ------ " + str(
                datetime.strptime(args['start'], '%Y-%m-%d')))
            company = self.env['res.company'].search([
                ('id', '=', args['id'])
            ], limit=1)
            fiel = self.env['cfdi.fiel'].search([
                ('company_id', '=', company.id),
                ('active', '=', True)], order='id',
                limit=1)
            # import ipdb; ipdb.set_trace()
            fiel = Fiel(base64.decodebytes(
                fiel.fiel_file),
                base64.decodebytes(fiel.fiel_key_file),
                fiel.fiel_password)
            auth = Autenticacion(fiel)
            token = auth.obtener_token()
            descarga = SolicitaDescarga(fiel)
            if args['tipo_solicitud'] == "Emisor":
                solicitud = descarga.solicitar_descarga(
                    token,
                    company.vat,
                    datetime.strptime(args['start'], '%Y-%m-%d'),
                    datetime.strptime(args['end'], '%Y-%m-%d'),
                    rfc_emisor=company.vat,
                    tipo_solicitud='CFDI')
            else:
                solicitud = descarga.solicitar_descarga(
                    token,
                    company.vat,
                    datetime.strptime(args['start'], '%Y-%m-%d'),
                    datetime.strptime(args['end'], '%Y-%m-%d'),
                    rfc_receptor=company.vat,
                    tipo_solicitud='CFDI')
            _logger.error("Error: 1 - SOLICITUD:: " + str(solicitud))
            while True:
                token = auth.obtener_token()
                # print('Error: TOKEN: ', token)
                verificacion = VerificaSolicitudDescarga(fiel)
                verificacion = verificacion.verificar_descarga(
                    token,
                    company.vat,
                    solicitud['id_solicitud'])

                _logger.error("Error: SOLICITUD::  " + str(verificacion))
                estado_solicitud = int(verificacion['estado_solicitud'])
                # 1, Aceptada
                # 2, En proceso
                # 3, Terminada
                # 4, Error
                # 5, Rechazada
                # 6, Vencida
                _logger.error("Error: EDO SOLICITUD::  " + str(estado_solicitud))
                if estado_solicitud <= 2:
                    # Si el estado de solicitud esta Aceptado o en proceso el programa espera
                    # 60 segundos y vuelve a tratar de verificar
                    time.sleep(10)
                    continue
                elif estado_solicitud >= 4:
                    _logger.error("Error: error general ")
                    break
                else:
                    if int(verificacion['numero_cfdis']) == 0:
                        break
                    # Si el estatus es 3 se trata de descargar los paquetes
                    for paquete in verificacion['paquetes']:
                        _logger.error("Error: PAQUETE: " + str(paquete))
                        descarga = DescargaMasiva(fiel)
                        _logger.error("Error: DESCARGA: " + str(descarga))
                        descarga = descarga.descargar_paquete(token, company.vat, paquete)
                        _logger.error("Error: DESCARGA: " + str(descarga))
                        return descarga
                        # with open('{}.zip'.format(paquete), 'wb') as fp:
                        #     return base64.b64decode(descarga['paquete_b64'])
                    break

        else:
            _logger.error("Error: SOLICITUD::  ------ DATA MISSING")
