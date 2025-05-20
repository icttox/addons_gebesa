# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, _, fields, models
from odoo.exceptions import UserError


class GebesaReconcileAdvance(models.Model):
    _name = 'gebesa.reconcile.advance'
    _inherit = ['mail.thread']
    _order = 'name asc'
    _rec_name = 'name'

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_('No puedes eliminar una concilacion en estatus Hecho'))
            return super().unlink()

    @api.model
    def default_get(self, fields):
        # context = context or {}
        res = super().default_get(fields)

        if not self._context.get('default_type', False):
            res.update({'type': 'pay'})

        return res

    # Obtiene la moneda de la compañia
    def _get_company_currency(self, adv_id):
        return self.env['gebesa.reconcile.advance'].browse(adv_id).move_id.\
            journal_id.company_id.currency_id.id

    # Obtiene la moneda conciliacion de anticipo si no tiene obtiene la moneda
    # de la compañia
    def _get_current_currency(self, exp_id):
        exp = self.env['gebesa.reconcile.advance'].browse('exp_id')
        return exp.currency_id.id or\
            self._get_company_currency('exp_id')

    def _get_journal(self):
        if self._context is None:
            self._context = {}
        type_inv = self._context.get('default_type', 'pay')
        # user = self.pool.get('res.users').browse(self._cr, self._uid,
        # self._uid,
        # context=self._context)
        user = self.env['res.users'].browse(self._uid)
        company_id = self._context.get('company_id', user.company_id.id)
        type2journal = {'out_invoice': 'sale', 'pay': 'purchase',
                        'out_refund': 'sale_refund',
                        'in_refund': 'purchase_refund'}
        # journal_obj = self.pool.get('account.journal')
        journal_obj = self.env['account.journal']
        domain = [('company_id', '=', company_id)]
        if isinstance(type_inv, list):
            domain.append(('type', 'in', [type2journal.get(type) for type in
                                          type_inv if type2journal.get(type)]))
        else:
            domain.append(('type', '=', type2journal.get(type_inv, 'sale')))
        # res = journal_obj.search(self._cr, self._uid, domain, limit=1)
        res = journal_obj.search(domain)
        return res and res[0] or False

    name = fields.Char(
        string='Name',
        size=256,
        help='Name of this Advance Document',
        track_visibility='onchange',
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        help='Document Date',
        track_visibility='onchange',
    )
    date_post = fields.Date(
        string='Accounting Date',
        default=fields.Date.today,
        help='Date to be used in Journal Entries when posted',
        track_visibility='onchange',
    )
    type = fields.Selection([
        ('pay', 'Payment'),
        ('rec', 'Receipt')],
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancel'),
        ('done', 'Done')],
        default='draft',
        help='State',
        track_visibility='onchange',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'gebesa.reconcile.advance'),
        help='Company',
        track_visibility='always',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        help='Advance Partner',
        track_visibility='onchange',
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        default=_get_journal,
        help='Accounting Journal where Entries will be posted',
        track_visibility='always',
    )
    move_id = fields.Many2one(
        'account.move',
        string='Accounting Entry',
        help='Accounting Entry',
        track_visibility='always',
        copy=False
    )
    invoice_ids = fields.Many2many(
        'account.invoice',
        string='Invoices',
        help='Invoices to be used in this Advance',
        copy=False
    )
    payment_ids = fields.Many2many(
        'account.payment',
        string='Advances',
        help='Advances to be used',
        copy=False
    )
    ai_aml_ids = fields.Many2many(
        'account.move.line',
        string='Invoice Entry Lines',
        copy=False
    )
    av_aml_ids = fields.Many2many(
        'account.move.line',
        string='Advance Entry Lines',
        copy=False
    )
    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Costs Center',
    )

    def invoice_credit_lines(self, amount, am_id=None,
                             account_id=False, partner_id=False, date=None,
                             name=None, analytic_id=False, moneda=False,
                             monto_moneda=False):
        aml_obj = self.env['account.move.line']
        # ids = isinstance(ids, (int, long)) and [ids] or ids
        ara_brw = self[0]
        account_id = account_id or \
            ara_brw.partner_id.property_account_payable_id.id
        partner_id = ara_brw.partner_id.id
        date = date or ara_brw.date_post or fields.date.today()
        vals = {
            'move_id': am_id or ara_brw.move_id.id,
            'journal_id': ara_brw.journal_id.id,
            'date': date,
            'debit': 0.0,
            'name': _(name),
            'partner_id': partner_id,
            'account_id': account_id,
            'analytic_account_id': analytic_id,
            'currency_id': moneda or False,
            'amount_currency': monto_moneda or False,
            'credit': amount,
        }

        new_line = aml_obj.with_context({'check_move_validity': False}).\
            create(vals)

        return new_line.id

    def invoice_debit_lines(self, amount, am_id=None,
                            account_id=False, partner_id=False, date=None,
                            name=None, analytic_id=False, moneda=False,
                            monto_moneda=False):
        aml_obj = self.env['account.move.line']
        # ids = isinstance(ids, (int, long)) and [ids] or ids
        ara_brw = self[0]
        account_id = account_id or \
            ara_brw.partner_id.property_account_payable_id.id
        partner_id = ara_brw.partner_id.id
        date = date or ara_brw.date_post or fields.date.today()
        vals = {
            'move_id': am_id or ara_brw.move_id.id,
            'journal_id': ara_brw.journal_id.id,
            'date': date,
            'debit': amount,
            'name': _(name),
            'partner_id': partner_id,
            'account_id': account_id,
            'analytic_account_id': analytic_id,
            'currency_id': moneda or False,
            'amount_currency': monto_moneda or False,
            'credit': 0.0,
        }

        new_line = aml_obj.with_context({'check_move_validity': False}).\
            create(vals)
        return new_line.id

    @api.multi
    def validate_data(self):
        # context = self._context or {}
        # ids = isinstance(ids, (int, long)) and [ids] or ids
        ara_brw = self[0]
        res = []
        res.append((ara_brw.invoice_ids or ara_brw.ai_aml_ids) and
                   True or False)
        res.append((ara_brw.payment_ids or ara_brw.av_aml_ids) and
                   True or ara_brw.av_aml_ids and True or False)

        if any([inv.date_invoice > self.date_post for inv in self.invoice_ids]):
            raise UserError(_(
                'Error!\nAll the invoices must be have a date after the post date.'))

        if any([pay.payment_date > self.date_post for pay in self.payment_ids]):
            raise UserError(_(
                'Error!\nAll the payments must be have a date after the post date.'))
        if all(res):
            return True
        raise UserError(_('Error!'
                          '\nPlease Field the Invoices & \
                            Advances Fields.'))

    @api.multi
    def payment_reconcile(self):
        context = self._context or {}
        self.validate_data()
        inv_obj = self.env['account.invoice']
        # aag_obj = self.env['account.account.global']
        pay_obj = self.env['account.payment']
        am_obj = self.env['account.move']
        aml_obj = self.env['account.move.line']
        cur_obj = self.env['res.currency']
        res = {}

        # El documento con los datos a conciliar
        ara_brw = self[0]

        # Valida, un solo anticipo por movimiento
        if len(ara_brw.payment_ids) > 1:
            raise UserError(_('For integration issues, only an advance is'
                              'allowed per application,'
                              '\nTo apply another advance will have to create'
                              'another application.'))

        # Valida que las facturas sean posteriores al anticipo
        for invoice in ara_brw.invoice_ids:
            if invoice.date_invoice > ara_brw.date:
                raise UserError(_('Invoices can not include a date subsequent'
                                  'to that of the Conciliation'))
            for advance in ara_brw.payment_ids:
                if advance.currency_id and invoice.currency_id:
                    if advance.currency_id.id != invoice.currency_id.id:
                        raise UserError(_('All Invoices and Advances must be'
                                          'registered in the same currency'
                                          '\nPlease verify...'))

        tot_cargos = 0.0
        for invoice in ara_brw.invoice_ids:
            tot_cargos += invoice.residual

        tot_abonos = 0.0
        for advance in ara_brw.payment_ids:
            tot_abonos += advance.pending_amount

        # Se crea el acocunt.move
        vals = {
            'date': ara_brw.date_post,
            'ref': ara_brw.name,
            'company_id': ara_brw.company_id.id,
            'journal_id': ara_brw.journal_id.id,
        }
        am_id = self.env['account.move'].create(vals)

        # Se obtienen las facturas de los proveedores incluidas en la
        # conciliacion, las facturas (deudas)
        # Las ordena en forma descendente en base a la fecha de vencimiento
        invoice_ids = ara_brw.invoice_ids.sorted(key=lambda rec: rec.date_due)

        # Se obtienen los payments (anticipos) incluidas en la conciliacion
        payment_ids = [pay.id for pay in ara_brw.payment_ids]
        # Las ordena en forma descendente en base a la fecha de vencimiento
        payment_ids.sort()

        lines_2_rec = []
        lines_2_par = []
        get_aml = ara_brw.type == 'pay' and self.invoice_debit_lines or \
            self.invoice_credit_lines
        create_tax = True
        if ara_brw.type == 'rec':
            create_tax = False
        sign = ara_brw.type == 'rec' and -1 or 1
        moneda_id = False
        suma_saldado = 0.0
        temp = []
        appl_inv = []
        num = -1

        while invoice_ids and tot_abonos and tot_abonos > 0:
            num += 1
            if len(invoice_ids) == num:
                break
            inv_brw = inv_obj.browse(invoice_ids[num].id)
            saldo = inv_brw.residual
            if inv_brw.currency_id and inv_brw.company_id.currency_id and \
                    inv_brw.currency_id.id != inv_brw.company_id.\
                    currency_id.id:
                moneda_id = inv_brw.currency_id.id
            ctx = context.copy()
            ctx.update({'date': inv_brw.date_invoice})
            if tot_abonos >= saldo:
                # creo la estructura de la linea contable pero con el importe
                # en pesos. Se salda completa la factura ya que los anticipos
                # lo cubren, se salda en moneda base con la paridad
                # a la fecha de la factura.
                # saldo_mxn = cur_obj.browse(
                #     inv_brw.currency_id.id).with_context(ctx).compute(
                #     inv_brw.residual,
                #     inv_brw.company_id.currency_id)
                saldo_mxn = cur_obj.browse(
                    inv_brw.currency_id.id)._convert(
                    inv_brw.residual,
                    inv_brw.company_id.currency_id,
                    inv_brw.company_id,
                    inv_brw.date_invoice)

                res[inv_brw.id] = inv_brw.residual

                # Mejor sacarlos de los asientos de la factura para que no haya
                # diferencias por centavos
                temp = []
                for move in am_obj.browse([inv_brw.move_id.id]):
                    for line in move.line_ids:
                        temp.append(line.id)

                # aml_pagos = []
                for linea_con in temp:
                    lic_brw = aml_obj.browse(linea_con)
                    if lic_brw.account_id.internal_type == 'payable' or \
                            lic_brw.account_id.internal_type == 'receivable' \
                            and not lic_brw.full_reconcile_id:

                        if lic_brw.tax_line_id.amount < 0:
                            continue

                        monto_libros = ara_brw.type == 'pay' and \
                            lic_brw.credit or lic_brw.debit

                        partial = self.env['account.partial.reconcile'].search(
                            ['|', ('credit_move_id', '=', lic_brw.id),
                             ('debit_move_id', '=', lic_brw.id)])

                        if abs(saldo_mxn - monto_libros) < 0.5 and not partial:
                            saldo_mxn = monto_libros

                        if moneda_id:
                            monto_mon = (inv_brw.residual * sign)
                        else:
                            monto_mon = False

                        aml_pago = get_aml(saldo_mxn,
                                           account_id=inv_brw.account_id.id,
                                           am_id=am_id.id,
                                           name=_('Application of advance '
                                                  'to invoice: ') +
                                           inv_brw.number, analytic_id=inv_brw.
                                           account_analytic_id.id,
                                           moneda=moneda_id,
                                           monto_moneda=monto_mon)
                        appl_inv.append(inv_brw.id)

                iamls = [line.id for line in inv_brw.move_id.line_ids if
                         line.account_id.internal_type == (ara_brw.type ==
                                                           'pay' and
                                                           'payable' or
                                                           'receivable')]
                # pamls = [line.id for line in inv_brw.payment_ids]
                pamls = []
                # Esto funciona solo cuando for linea_con in temp da una sola
                # iteracion poner atencion cuando de mas de una iteracion los
                # primeros aml_pago no los conciliará

                if len(pamls) > 0:
                    lines_2_par.append(iamls + pamls + [aml_pago])
                else:
                    lines_2_rec.append(iamls + pamls + [aml_pago])

                suma_saldado += saldo_mxn

                # invoice_ids.pop(0)
                tot_abonos -= inv_brw.residual

            else:
                # creo la estructura de la linea contable pero con el importe
                # en pesos. Se abona el resto de los anticipos, se abona en
                # moneda base a la fecha de la factura
                # pago_mxn = cur_obj.browse(
                #     inv_brw.currency_id.id).with_context(ctx).compute(
                #     tot_abonos,
                #     inv_brw.company_id.currency_id)
                pago_mxn = cur_obj.browse(
                    inv_brw.currency_id.id)._convert(
                    tot_abonos,
                    inv_brw.company_id.currency_id,
                    inv_brw.company_id,
                    inv_brw.date_invoice)

                res[inv_brw.id] = tot_abonos

                if moneda_id:
                    monto_mon = (tot_abonos * sign)
                else:
                    monto_mon = False

                aml_pago = get_aml(pago_mxn, account_id=inv_brw.
                                   account_id.id, am_id=am_id.id,
                                   name=_('Application of advance to '
                                          'invoice: ') +
                                   inv_brw.number, analytic_id=inv_brw.
                                   account_analytic_id.id, moneda=moneda_id,
                                   monto_moneda=monto_mon)
                appl_inv.append(inv_brw.id)

                iamls = [line.id for line in inv_brw.move_id.line_ids if line.
                         account_id.internal_type == (ara_brw.type == 'pay' and
                                                      'payable' or
                                                      'receivable')]

                # pamls = [line.id for line in inv_brw.payment_ids]
                pamls = []
                lines_2_par.append(iamls + pamls + [aml_pago])
                suma_saldado += pago_mxn
                # invoice_ids.pop(0)
                tot_abonos -= inv_brw.residual

        # Hacer lo mismo que las facturas pero para los anticipos
        adv_2_rec = []
        adv_2_par = []
        anticipos = {}
        get_aml = ara_brw.type == 'pay' and self.invoice_credit_lines or \
            self.invoice_debit_lines
        suma_aplicado = 0.0
        while tot_cargos and tot_cargos > 0 and payment_ids:
            pay_brw = pay_obj.browse(payment_ids[0])
            mov_brw = self.env['account.move.line'].search(
                              [('payment_id', '=', pay_brw.id)])
            saldo = pay_brw.pending_amount

            if pay_brw.currency_id and pay_brw.company_id.currency_id and\
                    pay_brw.currency_id.id !=\
                    pay_brw.company_id.currency_id.id:
                moneda_id = pay_brw.currency_id.id

            ctx = context.copy()
            ctx.update({'date': pay_brw.payment_date})
            if ara_brw.type == 'pay':
                # Obtengo la cuenta contable de anticipos del proveedor
                acc_id = ara_brw.partner_id.\
                    property_account_supplier_advance_id.id
            else:
                # Obtengo la cuenta contable de anticipos del cliente
                acc_id = ara_brw.partner_id.\
                    property_account_customer_advance_id.id

            av_aml_id = [lin.id
                         for lin in mov_brw
                         if (lin.account_id.id == acc_id) and
                         (not lin.full_reconcile_id or
                          lin.full_reconcile_id is None)]

            # if self.partner_id.supplier:
            #     advance_tax_id = self.env['ir.values'].get_default(
            #         'account.config.settings', 'advance_tax_id')
            # else:
            #     advance_tax_id = self.env['ir.values'].get_default(
            #         'account.config.settings', 'advance_tax_cust_id')

            if tot_cargos >= saldo:
                # Creo la estructura de la linea contable correspondiente a los
                # vouchers(anticipos), Con el monto de los anticipos aplicados
                # en Moneda Nacional
                # saldo_mxn = cur_obj.browse(
                #     pay_brw.currency_id.id).with_context(ctx).compute(
                #     pay_brw.pending_amount,
                #     pay_brw.company_id.currency_id)
                saldo_mxn = cur_obj.browse(
                    pay_brw.currency_id.id)._convert(
                    pay_brw.pending_amount,
                    pay_brw.company_id.currency_id,
                    pay_brw.company_id,
                    pay_brw.payment_date)

                for aml_brw in aml_obj.browse(av_aml_id):
                    libros_saldo = aml_brw[ara_brw.type ==
                                           'pay' and 'debit' or 'credit']

                    if abs(saldo_mxn - libros_saldo) < 0.5:
                        saldo_mxn = libros_saldo

                    if moneda_id:
                        monto_mon = (pay_brw.pending_amount *
                                     (sign * -1))
                    else:
                        monto_mon = False

                    # fecha = datetime.strptime(
                    #     pay_brw.payment_date, '%Y-%m-%d').date()

                    aplanti = get_aml(
                        saldo_mxn, account_id=acc_id,
                        am_id=am_id.id,
                        name=_('Application of advance: ') +
                        pay_brw.name,
                        analytic_id=pay_brw.account_analytic_id.id,
                        moneda=moneda_id, monto_moneda=monto_mon)
                    adv_2_rec.append([aml_brw.id] + [aplanti])

                suma_aplicado += saldo_mxn
                payment_ids.pop(0)
                tot_cargos -= pay_brw.pending_amount
                anticipos[pay_brw.id] = 0.0
            else:
                # pago_mxn = cur_obj.browse(
                #     pay_brw.currency_id.id).with_context(ctx).compute(
                #     tot_cargos,
                #     pay_brw.company_id.currency_id)
                pago_mxn = cur_obj.browse(
                    pay_brw.currency_id.id)._convert(
                    tot_cargos,
                    pay_brw.company_id.currency_id,
                    pay_brw.company_id,
                    pay_brw.payment_date)
                if moneda_id:
                    monto_mon = (tot_cargos * (sign * -1))
                else:
                    monto_mon = False
                # fecha = datetime.strptime(
                #     pay_brw.payment_date, '%Y-%m-%d').date()
                # account = aag_obj.search(
                #     [('name', '=', 'anti_clie_ext'),
                #      ('code', '=', 1)], limit=1).account_id.id
                # if ara_brw.type == 'rec' and fecha >\
                #         datetime.strptime('2015-09-14', '%Y-%m-%d').date() and\
                #         acc_id != account:
                #     # Generar IVA Repercutido por la cantidad que se dio de
                #     # anticipo
                #     # Warning de HardCode
                #     impuesto_brw = self.env['account.tax'].browse(
                #         advance_tax_id)
                #     porcentaje = (impuesto_brw.amount / 100)
                #     cta_cont = impuesto_brw.account_id.id
                #     monto = round(porcentaje * (pago_mxn / (1 + porcentaje)),
                #                   6)
                #     pago_mxn_untax = pago_mxn - monto
                #     self.invoice_debit_lines(monto,
                #                              account_id=cta_cont,
                #                              am_id=am_id.id,
                #                              name=impuesto_brw.name + ': ' +
                #                              pay_brw.name,
                #                              analytic_id=pay_brw.
                #                              account_analytic_id.id)

                #     aml_aplic = get_aml(pago_mxn_untax,
                #                         account_id=acc_id,
                #                         am_id=am_id.id,
                #                         name=_('Application of advance: ') +
                #                         pay_brw.name,
                #                         analytic_id=pay_brw.
                #                         account_analytic_id.id,
                #                         moneda=moneda_id,
                #                         monto_moneda=monto_mon)
                # else:
                aml_aplic = get_aml(pago_mxn,
                                    account_id=acc_id,
                                    am_id=am_id.id,
                                    name=_('Application of advance: ') +
                                    pay_brw.name,
                                    analytic_id=pay_brw.
                                    account_analytic_id.id,
                                    moneda=moneda_id,
                                    monto_moneda=monto_mon)
                adv_2_par.append([aml_aplic, av_aml_id[0]])
                suma_aplicado += pago_mxn
                payment_ids.pop(0)
                resto = pay_brw.pending_amount - tot_cargos
                tot_cargos -= pay_brw.pending_amount
                anticipos[pay_brw.id] = resto

        # Parto del supuesto que el dolar siempre esta ganando terreno contra
        # el peso por lo tanto infiero que la mayoria del tiempo será ganancia
        # cambiaria Por anticipar el pago, pago menos por la factura que en un
        # futuro costará mas, Asi que calculo la ganancia, en caso de que
        # dif_tipocam sea negativo
        # Entonces es perdida cambiaria, de lo contrario es ganancia
        dif_tipocam = suma_aplicado - suma_saldado

        if abs(dif_tipocam) > 0.01:
            if ara_brw.type == 'pay':
                writeoff_acc_id = self.env['res.company'].browse(
                    ara_brw.company_id.id).\
                    expense_currency_exchange_account_id.id

                get_aml = dif_tipocam > 0 and self.invoice_debit_lines or \
                    self.invoice_credit_lines
                aml_aplic = get_aml(abs(dif_tipocam),
                                    account_id=writeoff_acc_id,
                                    am_id=am_id.id,
                                    name='Diferencia cambiaria',
                                    analytic_id=ara_brw.account_analytic_id.id)
            else:
                writeoff_acc_id = self.env['res.company'].browse(
                    ara_brw.company_id.id).\
                    income_currency_exchange_account_id.id

                get_aml = dif_tipocam < 0 and self.invoice_debit_lines or \
                    self.invoice_credit_lines
                aml_aplic = get_aml(abs(dif_tipocam),
                                    account_id=writeoff_acc_id,
                                    am_id=am_id.id,
                                    name='Diferencia cambiaria',
                                    analytic_id=ara_brw.account_analytic_id.id)

        if len(lines_2_par) > 0 and len(lines_2_rec) == 0 and len(adv_2_rec) >\
                0 and len(adv_2_par) == 0:
            adv_2_par = adv_2_rec
            adv_2_rec = []

        am_id.post()

        # Realiza la conciliacion Total
        ctx = context.copy()
        ctx.update({'create_tax': create_tax})
        for line_pair in adv_2_rec + lines_2_rec:
            if not line_pair:
                continue
            aml_obj.browse(line_pair).with_context(ctx).reconcile(False, ara_brw.journal_id.id)

        # Realiza conciliacion parcial
        for line_pair in adv_2_par + lines_2_par:
            if not line_pair:
                continue
            aml_obj.browse(line_pair).with_context(ctx).reconcile()
        ara_brw.write({'move_id': am_id.id, 'state': 'done'})

        for k, v in anticipos.items():
            pay = self.env['account.payment'].search(
                          [('id', '=', k)])
            pay.write({'pending_amount': v})

        return res

    @api.multi
    def action_draft_advance(self):
        self.validate_data()
        ara_brw = self[0]

        if not self.env.user.has_group(
                'gebesa_reconcile_advance.group_cancel_advance_reconcile'):
            raise UserError(_('Error!\nYou do not have privileges to \
                            disengage an advance.\nCheck with your \
                            system administrator.'))
        for anticipo in ara_brw.payment_ids:

            monto_desc = 0.0
            # Recorror las lineas contables del pago o anticipo
            for linea_con in anticipo.move_line_ids:
                # Verifica si tiene concilaciones del lado del debe
                if linea_con.matched_debit_ids:
                    # Recore las lineas contebles de las partial_reconcile
                    for rec in linea_con.matched_debit_ids.debit_move_id:
                        # Verifica que la liena este en la poliza de
                        # la concileacion
                        if rec in ara_brw.move_id.line_ids:
                            if rec.amount_currency:
                                monto_desc += abs(rec.amount_currency)
                            else:
                                monto_desc += rec.debit + \
                                    rec.credit
                # Verifica si tiene concilaciones del lado del haber
                if linea_con.matched_credit_ids:
                    # Recore las lineas contebles de las partial_reconcile
                    for credit in linea_con.matched_credit_ids:
                        for rec in credit.credit_move_id:
                            # Verifica que la liena este en la poliza de
                            # la concileacion
                            if rec in ara_brw.move_id.line_ids:
                                if rec.amount_currency:
                                    monto_desc += abs(rec.amount_currency)
                                else:
                                    monto_desc += rec.debit + \
                                        rec.credit

            pendiente_nuevo = anticipo.pending_amount + monto_desc
            anticipo.pending_amount = pendiente_nuevo

        for advance in self:
            advance.refresh()
            for line in advance.move_id.line_ids:
                line.remove_move_reconcile()
            if advance.move_id:
                advance.move_id.button_cancel()
                advance.move_id.unlink()

            advance.state = 'draft'
            advance.move_id = False

        return True
