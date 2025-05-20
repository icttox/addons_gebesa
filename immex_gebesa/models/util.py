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
import datetime
import tempfile
import base64
import hashlib
import subprocess
import M2Crypto
from M2Crypto import RSA
from OpenSSL import crypto as c


def get_sello_cadena_sha256(path_pem, texto):
    keys = RSA.load_key(path_pem)
    cadena_original = texto.encode('utf-8')
    digest = hashlib.new('sha256', cadena_original).digest()
    gkey = base64.b64encode(keys.sign(digest, "sha256"))
    return gkey


def b64str_to_tempfile(b64_str=None, file_suffix=None,
                       file_prefix=None):
    """
    @param b64_str : Text in Base_64 format for add in the file
    @param file_suffix : Sufix of the file
    @param file_prefix : Name of file in TempFile
    """
    (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
    with open(fname, 'wb') as f_read:
        # f_read.write(base64.decodestring(b64_str or ''))
        f_read.write(base64.b64decode(b64_str or ''))
    os.close(fileno)
    return fname


def convert_key_cer_to_pem(key, password):
    # TODO compute it from a python way
    com = 'openssl pkcs8 -in %s -inform der -outform pem -out %s -passin file:%s'
    with tempfile.NamedTemporaryFile('wb', suffix='.key', prefix='edi.mx.tmp.') as key_file, \
            tempfile.NamedTemporaryFile('wb', suffix='.txt', prefix='edi.mx.tmp.') as pwd_file, \
            tempfile.NamedTemporaryFile('rb', suffix='.key', prefix='edi.mx.tmp.') as keypem_file:
        key_file.write(key)
        key_file.flush()
        pwd_file.write(password)
        pwd_file.flush()
        subprocess.call((com % (key_file.name, keypem_file.name, pwd_file.name)).split())
        key_pem = keypem_file.read()
    return key_pem


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
    result = ''
    if type_der == 'cer':
        result = M2Crypto.X509.load_cert_string(
            base64.b64decode(fname_der),
            M2Crypto.X509.FORMAT_DER).as_pem()
    elif type_der == 'key':
        result = convert_key_cer_to_pem(
            base64.b64decode(fname_der), fname_password_der)
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
            cert.get_notBefore().decode("utf-8"), "%Y%m%d%H%M%SZ")
        date_end = datetime.datetime.strptime(
            cert.get_notAfter().decode("utf-8"), "%Y%m%d%H%M%SZ")
        result["notBefore"] = date_start
        result["notAfter"] = date_end
    if 'serial' in params:
        result = str(u'{0:0>40x}'.format(cert.get_serial_number()))
    return result
