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

import os
import time
import datetime
import subprocess
import tempfile
import base64
import hashlib
from xml.etree import ElementTree as ET
import lxml.etree as XET
from settings import PRE
from settings import log
import M2Crypto
from M2Crypto import RSA
from OpenSSL import crypto as c


def mkdir(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)


def now(minutes=0):
    d_now = datetime.datetime.now() - datetime.timedelta(minutes=minutes)
    return d_now.isoformat()[:19]


def call(args):
    return subprocess.check_output(args, shell=True).decode()


def get_cer(path_cer):
    path = os.path.join(os.getcwd(), path_cer)
    args = 'openssl enc -base64 -in {}'.format(path)
    return call(args).replace('\n', '')


def get_serie(path_cer):
    path = os.path.join(os.getcwd(), path_cer)
    args = 'openssl x509 -inform DER -in {} -noout -serial'.format(path)
    return call(args).split('=')[1][1::2]


def get_sello(path_xml, path_xslt, path_pem):
    args = 'xsltproc {0} {1} | openssl dgst -sha1 -sign {2} | ' \
        'openssl enc -base64 -A'.format(path_xslt, path_xml, path_pem)
    return call(args)


def get_selloa(path_xml, path_xslt, path_pem):
    keys = RSA.load_key(path_pem)
    cadena_original = generate_cadena_original(path_xslt, path_xml)
    digest = hashlib.new('sha1', cadena_original).digest()
    gkey = base64.b64encode(keys.sign(digest, "sha1"))
    return gkey


def get_sello_cadena(path_pem, texto):
    keys = RSA.load_key(path_pem)
    cadena_original = texto
    digest = hashlib.new('sha1', cadena_original).digest()
    gkey = base64.b64encode(keys.sign(digest, "sha1"))
    return gkey


def get_sello_cadena_sha256(path_pem, texto):
    keys = RSA.load_key(path_pem)
    cadena_original = texto
    digest = hashlib.new('sha256', cadena_original).digest()
    gkey = base64.b64encode(keys.sign(digest, "sha256"))
    return gkey


def generate_cadena_original(path_xslt, path_xml):
    xml = read_file(path_xml)
    dom = XET.fromstring(xml)
    xslt = XET.parse(path_xslt)
    transform = XET.XSLT(xslt)
    return str(transform(dom))


def generate_cadena_original_fromstr(path_xslt, texto):
    dom = XET.fromstring(str(texto))
    xslt = XET.parse(path_xslt)
    transform = XET.XSLT(xslt)
    return str(transform(dom))


def get_epoch():
    epo = int(time.mktime(datetime.datetime.now().timetuple()))
    return epo


def save_file(path, data, mode='w'):
    file_tmp = open(path, mode)
    if isinstance(data, str):
        file_tmp.write(data)
    else:
        file_tmp.write(data.decode('utf-8'))
    file_tmp.close()


def read_file(path_xml):
    with open(path_xml, 'r') as fie:
        data = fie.read()
    return data


def make_data(invoice):
    data = {}
    try:
        tree = ET.parse(invoice).getroot()
        version = tree.attrib['version']
        node = tree.find('{}Emisor'.format(PRE[version]))
        data['total'] = tree.attrib['total']
        data['emisor_rfc'] = node.attrib['rfc']
        node = tree.find('{}Receptor'.format(PRE[version]))
        data['receptor_rfc'] = node.attrib['rfc']
        node = tree.find(
            '{}Complemento/{}TimbreFiscalDigital'.format(
                PRE[version], PRE['TIMBRE']))
        data['uuid'] = node.attrib['UUID']
        return data
    except Exception as exc:
        log.error('La factura no se pudo parsear, '
                  'asegurate de que sea un CFDI válido')
        log.debug(exc)
        return {}


def b64str_to_tempfile(b64_str=None, file_suffix=None,
                       file_prefix=None):
    """
    @param b64_str : Text in Base_64 format for add in the file
    @param file_suffix : Sufix of the file
    @param file_prefix : Name of file in TempFile
    """
    (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
    f_read = open(fname, 'wb')
    f_read.write(base64.decodebytes(b64_str or ''))
    f_read.close()
    os.close(fileno)
    return fname


def exec_command_pipe(args):
    # Agregue esta funcion, ya que con la nueva funcion original,
    # de tools no funciona
    # TODO: Hacer separacion de argumentos, no por espacio, sino tambien por "
    # ", como tipo csv, pero separator espace & delimiter "
    cmd = ' '.join(args)
    if os.name == "nt":
        cmd = cmd.replace(
            '"', '')  # provisionalmente, porque no funcionaba en win32
    return os.popen2(cmd, 'b')


def _transform_der_to_pem(fname_der, fname_password_der=None,
                          type_der='cer'):
    """
    @param fname_der : File.cer configurated in the company
    @param fname_out : Information encrypted in Base_64from certificate
        that is send
    @param fname_password_der : File that contain the password configurated
        in this Certificate
    @param type_der : cer or key
    """
    cmd = ''
    com = 'openssl pkcs8 -inform DER -outform PEM -in "%s" -passin file:%s' % (
        fname_der, fname_password_der)
    result = ''
    if type_der == 'cer':
        result = M2Crypto.X509.load_cert_string(
            base64.decodebytes(fname_der),
            M2Crypto.X509.FORMAT_DER).as_pem()
    elif type_der == 'key':
        cmd = com
    if cmd:
        args = list(tuple(cmd.split(' ')))
        inputs, output = exec_command_pipe(args)
        result = output.read()
        inputs.close()
        output.close()
    return result


def _get_param_serial(fname, types='DER'):
    """
    @param fname : File.PEM with the information of the certificate
    @param fname_out : File.xml that is send
    """
    result = _get_params(fname, params=['serial'], types=types)
    result = result and result.replace('serial=', '').replace(
        '33', 'B').replace('3', '').replace('B', '3').replace(
        ' ', '').replace('\r', '').replace('\n', '').replace(
        '\r\n', '') or ''
    return result


def _get_param_dates(fname, date_fmt_return='%Y-%m-%d %H:%M:%S',
                     types='DER'):
    """
    @param fname : File.cer with the information of the certificate
    @params fname_out : Path and name of the file.txt with info encrypted
    @param date_fmt_return : Format of the date used
    @param type : Type of file
    """
    result_dict = _get_params(fname, params=['dates'], types=types)
    translate_key = {
        'notAfter': 'enddate',
        'notBefore': 'startdate',
    }
    result2 = {}
    if result_dict:
        for key in result_dict:
            date = result_dict[key]
            date_fmt = date.strftime(date_fmt_return)
            result2[translate_key[key]] = date_fmt
    return result2


def _get_params(fname, params=None, types='DER'):
    """
    @params: list [noout serial startdate enddate subject issuer dates]
    @type: str DER or PEM
    """
    result = {}
    cert = c.load_certificate(c.FILETYPE_PEM, base64.decodebytes(fname))
    if 'dates' in params:
        date_start = datetime.datetime.strptime(
            cert.get_notBefore(), "%Y%m%d%H%M%SZ")
        date_end = datetime.datetime.strptime(
            cert.get_notAfter(), "%Y%m%d%H%M%SZ")
        result["notBefore"] = date_start
        result["notAfter"] = date_end
    if 'serial' in params:
        result = str(u'{0:0>40x}'.format(cert.get_serial_number()))
    return result
