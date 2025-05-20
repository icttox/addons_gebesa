# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models
class ResPac(models.Model):
    _name = 'res.pac'
    _description = 'descripcion pendiente'

    name = fields.Char(help='Name for this PAC')

    active = fields.Boolean(
        help='Indicate if this pac is active', default=True)

    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        help='Company where will configured this pac',
        default=lambda self: self.env.user.company_id)

    user = fields.Char(
        help='User name for login in PAC server.')

    password = fields.Char(
        help='Password user for login in this PAC server.')

    url_webservice_sign = fields.Char(
        'URL Web Service Sign',
        help='Web Service URL used for send to sign the XML to PAC')

    url_webservice_cancel = fields.Char(
        'URL Web Service Cancel',
        help='Web Service URL used for send to cancel the XML to PAC')

    test_env = fields.Boolean(
        string='Test environment',
        help='Indicates that the PAC is intended to be used on a test '
             'environment, which may be used to avoid some validations',
        default=False)
