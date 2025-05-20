#!/usr/bin/env python3
# coding: utf-8
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# Contact: public ARROBA mauriciobaeza PUNTO net

import logging

DEBUG = True

TIMEOUT = 10

FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
DATE = '%d/%m/%Y %H:%M:%S'
logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt=DATE)
log = logging.getLogger('CFDI')

# No cambies este valor
RFC_PRUEBAS = 'AAA010101AAA'
VERSION = '3.2'
TIPO_COMPROBANTE = ('ingreso', 'egreso', 'traslado')
LOG = {
    'NAME': 'CFDI',
    'FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'DATE': '%d/%m/%Y %H:%M:%S',
}
SCHEMA = {
    '3.2': 'http://www.sat.gob.mx/cfd/3'
    'http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv32.xsd'
}
PRE = {
    '3.2': '{http://www.sat.gob.mx/cfd/3}',
    'TIMBRE': '{http://www.sat.gob.mx/TimbreFiscalDigital}',
}

PATH = {
    'CER': '/tmp/tmp.cer',
    'PEM': '/tmp/tmp.key.pem',
    'XSLT': 'bin/cadena3.2.xslt',
    'XML': '/tmp/fac_temp.xml',
}

SAT = {
    'CFDI': 'http://www.sat.gob.mx/cfd/3',
    'XSI': 'http://www.w3.org/2001/XMLSchema-instance',
    'SCHEMA': (
        'http://www.sat.gob.mx/cfd/3 '
        'http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv32.xsd'),
}
