# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from .common import MexicoReportsTestCase


class ResPartner(MexicoReportsTestCase):

    def test_001_type_third_04(self):
        """Verify that if partner country is Mexico, is assigned 04, to
        National Suppliers"""
        self.partner.write({
            'country_id': self.country_mx.id,
        })
        self.assertEquals(
            self.partner.l10n_mx_type_of_third, '04', 'Bad type of third')

    def test_002_type_third_05(self):
        """Verify that if partner country is != Mexico, is assigned 05, to
        Foreign Suppliers"""
        self.partner.write({
            'country_id': self.country_usa.id,
        })
        self.assertEquals(
            self.partner.l10n_mx_type_of_third, '05', 'Bad type of third')

    def test_003_inverse_demonym(self):
        """Test nationality and demonym fields of partner and country"""
        partner_es = self.partner.with_context(lang='es_MX')
        partner_en = self.partner

        self.assertEqual('Mexican', partner_en.country_id.demonym)
        self.assertEqual('Mexicano', partner_es.country_id.demonym)
        self.assertEqual('Mexicano', partner_en.l10n_mx_nationality)
        self.assertEqual('Mexicano', partner_es.l10n_mx_nationality)

        partner_en.write({'l10n_mx_nationality': 'Mejicano'})
        self.assertEqual('Mejicano', partner_es.country_id.demonym)
        self.assertEqual('Mexican', partner_en.country_id.demonym,
                         "Value was changed from source not just translation")
