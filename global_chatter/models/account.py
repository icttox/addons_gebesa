# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = ['message.post.show.all', 'account.payment']


class AccountAccount(models.Model):
    _name = 'account.account'
    #'mail.thread',
    _inherit = ['message.post.show.all', 'account.account']


class AccountMove(models.Model):
    _name = 'account.move'
    #  'mail.thread',
    _inherit = ['message.post.show.all', 'account.move']


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['message.post.show.all', 'account.invoice']
