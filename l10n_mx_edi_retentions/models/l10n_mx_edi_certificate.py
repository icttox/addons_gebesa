# Copyright 2021, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import base64
import logging
from odoo import api, models
_logger = logging.getLogger(__name__)
try:
    from OpenSSL import crypto
except ImportError:
    _logger.warning('OpenSSL library not found. If you plan to use l10n_mx_edi, please install the library from https://pypi.python.org/pypi/pyOpenSSL')


class L10nMxEdiCertificate(models.Model):
    _name = 'l10n_mx_edi.certificate'
    _inherit = 'l10n_mx_edi.certificate'

    @api.multi
    def get_encrypted_cadena_retention(self, cadena):
        '''Encrypt the cadena using the private key.
        '''
        self.ensure_one()
        key_pem = self.get_pem_key(self.key, self.password)
        private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, key_pem)
        encrypt = 'SHA1WithRSAEncryption'
        cadena_crypted = crypto.sign(private_key, cadena, encrypt)
        return base64.b64encode(cadena_crypted)
