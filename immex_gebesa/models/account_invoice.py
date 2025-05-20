# -*- coding: utf-8 -*-

import re
from datetime import datetime
from odoo import _, api, models, fields
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    country_fiscal_code = fields.Char(
        string='Codigo fiscal',
        related='partner_id.country_id.fiscal_code',
        readonly=True,
    )

    company_country_code = fields.Char(
        string='Codigo del pais de la compañia',
        related='company_id.country_id.code',
        readonly=True,
    )

    patente_aduanal = fields.Char(
        string='Patente aduanal',
        copy=False,
    )
    clave_aduanal = fields.Char(
        string='Clave aduanal',
        copy=False,
    )
    entry_date = fields.Datetime(
        string='Fecha de entrada',
        copy=False,
    )
    cove = fields.Char(
        string='COVE',
    )
    clave_pedimento = fields.Selection([
        ('IN', 'IN'),
        ('V1', 'V1'),
        ('AF', 'AF'),
        ('RT', 'RT')],
        string='Clave pedimento',
        track_visibility='always')

    descargue_ids = fields.One2many(
        'l10n.mx.immex.partida.descargue',
        'invoice_id',
        string='Descargue',
        copy=False
    )

    factura_ids = fields.One2many(
        'l10n.mx.immex.pedimento.factura',
        'invoice_id',
        string='Pedimentos Expo',
        readonly=True,
    )

    @api.depends('partner_id', 'clave_pedimento')
    def _compute_need_external_trade(self):
        """Assign the "Need external trade?" value how in the partner"""
        for record in self.filtered(lambda i: i.type == 'out_invoice'):
            if record.clave_pedimento != 'RT':
                record.l10n_mx_edi_external_trade = record.partner_id.l10n_mx_edi_external_trade
            else:
                record.l10n_mx_edi_external_trade = False

    @api.depends('l10n_mx_edi_external_trade', 'clave_pedimento')
    def _compute_l10n_mx_edi_export(self):
        for inv in self:
            if not inv.l10n_mx_edi_external_trade:
                if inv.clave_pedimento == 'RT':
                    inv.l10n_mx_edi_export = '03'
                else:
                    inv.l10n_mx_edi_export = '01'
            else:
                inv.l10n_mx_edi_export = '02'

    @api.onchange('petition_number')
    def _onchange_petition_number(self):
        pattern = re.compile("([0-9]{7}$)")
        if self.petition_number:
            if not pattern.match(self.petition_number):
                self.petition_number = ''
                warning_mess = {
                    'title': _('Validation Error'),
                    'message': _('Please enter valid Petiment number.')
                }
                return {'warning': warning_mess}
        return {}

    @api.onchange('patente_aduanal')
    def _onchange_patente_aduanal(self):
        pattern = re.compile("([0-9]{4}$)")
        if self.patente_aduanal:
            if not pattern.match(self.patente_aduanal):
                self.patente_aduanal = ''
                warning_mess = {
                    'title': _('Validation Error'),
                    'message': _('Please enter valid Customs Patent.')
                }
                return {'warning': warning_mess}
        return {}

    @api.onchange('clave_aduanal')
    def _onchange_clave_aduanal(self):
        pattern = re.compile("([0-9]{3}$)")
        if self.clave_aduanal:
            if not pattern.match(self.clave_aduanal):
                self.clave_aduanal = ''
                warning_mess = {
                    'title': _('Validation Error'),
                    'message': _('Please enter valid Customs code.')
                }
                return {'warning': warning_mess}
        return {}

    @api.multi
    def create_descargue(self):
        descargue_obj = self.env['l10n.mx.immex.partida.descargue']
        partidas_obj = self.env['l10n.mx.immex.partida']
        company_id = self.env.user.company_id.id
        self._cr.execute("""
            WITH RECURSIVE bom_detail(invoice_line_id,product_id,immex_type_id,qty,company_id,exceptions_apply,download_immex,lv) AS(
                SELECT
                    ail.id,
                    pp.id,
                    pt.immex_type_id,
                    ail.quantity,
                    %s,
                    ipt.download_exceptions_apply,
                    pt.apply_download_immex,
                    LPAD(CAST(ROW_NUMBER() OVER (ORDER BY ail.id) AS TEXT), 3, '0')
                FROM account_invoice ai
                JOIN account_invoice_line ail ON ai.id = ail.invoice_id
                JOIN product_product AS pp ON ail.product_id = pp.id
                JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN l10n_mx_immex_partida_type AS ipt ON pt.immex_type_id = ipt.id
                WHERE ai.id = %s AND ail.quantity > 0
                UNION SELECT
                    bd.invoice_line_id,
                    pp.id,
                    pt.immex_type_id,
                    ROUND(bd.qty * ((mb.product_qty * mbl.product_qty) / mb.product_qty),6),
                    bd.company_id,
                    ipt.download_exceptions_apply,
                    bd.download_immex,
                    CONCAT(bd.lv, '.', LPAD(CAST(ROW_NUMBER() OVER (ORDER BY bd.invoice_line_id,mbl.id) AS TEXT), 3, '0'))
                FROM bom_detail AS bd
                JOIN mrp_bom AS mb on bd.product_id = mb.product_id
                    AND bd.company_id = mb.company_id AND mb.active IS True
                LEFT JOIN mrp_bom_line AS mbl on mb.id = mbl.bom_id
                LEFT JOIN product_product AS pp ON mbl.product_id = pp.id
                JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN l10n_mx_immex_partida_type AS ipt ON pt.immex_type_id = ipt.id)
            SELECT product_id,SUM(qty),immex_type_id,invoice_line_id FROM bom_detail
            WHERE immex_type_id IS NOT NULL
                AND (exceptions_apply IS NOT TRUE OR (exceptions_apply IS TRUE AND download_immex IS TRUE))
            GROUP BY invoice_line_id,product_id,immex_type_id""", (
            [company_id, self.id]))
        products_immex = self._cr.fetchall()
        if products_immex:
            for product_immex in products_immex:
                partidas = partidas_obj.search([
                    ('immex_type_id', '=', product_immex[2]),
                    ('amount', '>', 0.00)])
                partidas = partidas.filtered(
                    lambda x: x.porcentaje_desperdicio < (
                        (100 * x.amount) / float(x.cantidad_udm_comercial)))
                if not partidas:
                    continue
                self.clave_pedimento = 'RT'
                descargue_id = descargue_obj.search([
                    ('invoice_id', '=', self.id),
                    ('invoice_line_id', '=', product_immex[3]),
                    ('product_id', '=', product_immex[0]),
                    ('partida_type_id', '=', product_immex[2])])
                if descargue_id:
                    descargue_id.quantity += product_immex[1]
                else:
                    descargue = descargue_obj.create({
                        'invoice_id': self.id,
                        'invoice_line_id': product_immex[3],
                        'product_id': product_immex[0],
                        'partida_type_id': product_immex[2],
                        'quantity': product_immex[1],
                    })
                    descargue.invoice_line_id.product_id.salida_a24 = True

    @api.multi
    def immex_remove_descargue(self):
        for invoice in self:
            for descargue in invoice.descargue_ids:
                for line in descargue.line_ids:
                    line.partida_id.amount += line.quantity
                    line.unlink()
                descargue.unlink()

    @api.multi
    def immex_descargue(self):
        partidas_obj = self.env['l10n.mx.immex.partida']
        uom_obj = self.env['uom.uom']
        factor_obj = self.env['product.uom.factor']
        line_obj = self.env['l10n.mx.immex.partida.descargue.line']
        for invoice in self:
            if not invoice.descargue_ids:
                invoice.create_descargue()

            if not invoice.descargue_ids:
                continue
            if any(line.id not in invoice.descargue_ids.mapped(
                    'invoice_line_id').mapped('id') for line in invoice.invoice_line_ids):
                raise ValidationError(_(
                    'No se puede facturar productos de RT con productos que no lo son'))

            for descargue in invoice.descargue_ids:
                if descargue.line_ids:
                    continue
                partidas = partidas_obj.search([
                    ('immex_type_id', '=', descargue.partida_type_id.id),
                    ('amount', '>', 0.00)])
                partidas = partidas.filtered(
                    lambda x: x.porcentaje_desperdicio < (
                        (100 * x.amount) / float(x.cantidad_udm_comercial)))
                quantity = descargue.quantity
                for partida in partidas:
                    if quantity <= 0:
                        continue
                    uom_id = uom_obj.search([
                        ('fiscal_code', '=', partida.udm_comercial)],
                        limit=1, order='id')
                    factor_id = factor_obj.search([
                        ('unmed_origin_id', '=', descargue.product_id.uom_id.id),
                        ('unmed_dest_id', 'in', uom_id.ids)])
                    if not factor_id:
                        raise ValidationError(_('No se encontro un factor de \
                            conversion para el producto %s de %s a %s') % (
                            descargue.product_id.default_code,
                            descargue.product_id.uom_id.name, uom_id.name))

                    detail = factor_id.mapped('details_ids').filtered(
                        lambda r: r.product_id.id == descargue.product_id.id)

                    if not detail:
                        raise ValidationError(_('No se encontro un detalle de \
                            conversion para el producto %s de %s a %s') % (
                            descargue.product_id.default_code,
                            descargue.product_id.uom_id.name, uom_id.name))

                    if not detail.factor > 0.0:
                        raise ValidationError(_('El factor del detalle de \
                            conversion para el producto %s de %s a %s debe ser \
                            mayor a 0') % (
                            descargue.product_id.default_code,
                            descargue.product_id.uom_id.name, uom_id.name))

                    quantity = quantity * detail.factor

                    if quantity <= partida.amount - (float(
                            partida.cantidad_udm_comercial) * (
                                partida.porcentaje_desperdicio / 100)):
                        partida.amount -= quantity
                        line_obj.create({
                            'descargue_id': descargue.id,
                            'partida_id': partida.id,
                            'quantity': quantity
                        })
                        quantity -= quantity

                    else:
                        quantity_partial = (partida.amount - (
                            float(partida.cantidad_udm_comercial) * (
                                partida.porcentaje_desperdicio / 100)))
                        # parte_decimal, parte_entera = math.modf(quantity_partial)
                        # quantity_partial = parte_entera * detail.factor
                        quantity -= quantity_partial
                        line_obj.create({
                            'descargue_id': descargue.id,
                            'partida_id': partida.id,
                            'quantity': quantity_partial
                        })
                        partida.amount -= quantity_partial

                    quantity = quantity / detail.factor

                if not descargue.line_ids:
                    raise ValidationError(_(
                        'No se puede facturar productos de RT con productos que no lo son'))
                descargue.qty_pending = quantity or 0.0

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            if invoice.partner_id.country_id.code != 'MX' and \
                    invoice.type == 'out_invoice' and \
                    invoice.partner_id.omitir_rt is not True:
                invoice.immex_descargue()
        return super().invoice_validate()

    @api.multi
    def action_cancel(self):
        self.immex_remove_descargue()
        return super().action_cancel()

    @api.model
    def send_email_invoice_rt_alert(self):
        inv_rt = self.search([
            ('clave_pedimento', '=', 'RT'),
            ('state', 'in', ['open', 'paid'])])
        if not inv_rt:
            return
        hoy = datetime.today()
        table = ''
        for invoice in inv_rt:
            limit_date = invoice.date_invoice
            days = hoy - fields.Datetime.from_string(limit_date)
            days = days.days
            date_state = invoice.state.encode('utf8')
            if invoice.state == 'paid':
                date_state = 'pagado'
            if invoice.state == 'open':
                date_state = 'abierto'
            for line_invoice in invoice.invoice_line_ids:
                if line_invoice:
                    descargue_ids = self.env['l10n.mx.immex.partida.descargue'].search([('invoice_line_id', '=', line_invoice.id)])
                    for descargue in descargue_ids:
                        if descargue:
                            for line_descargue in descargue.line_ids:
                                if line_descargue:
                                    clave_documento = self.env['l10n.mx.immex.pedimento'].search([
                                        ('num_pedimento', '=', line_descargue.partida_id.num_pedimento),
                                        ('patente', '=', line_descargue.partida_id.patente),
                                        ('clave_aduana', '=', line_descargue.partida_id.clave_aduana)])
                                    uom_tarifa = self.env['uom.uom'].search([('fiscal_code', '=', line_descargue.partida_id.udm_tarifa)], limit=1)
                                    uom_comercial = self.env['uom.uom'].search([('fiscal_code', '=', line_descargue.partida_id.udm_comercial)], limit=1)
                                    factor = line_descargue.quantity / descargue.quantity
                                    if days <= 1:
                                        table += """
                                            <tr><td align="left" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="center" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="left" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="left" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="center" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">[%s]</td>
                                            <td align="left" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="left" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">[%s]</td>
                                            <td align="left" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="center" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="right" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="center" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="left" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="center" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="center" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="center" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="right" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="right" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="right" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="right" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="right" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="right" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="center" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td>
                                            <td align="center" style="padding:5px 10px 5px 5px; font-size:15px;font-family:'Arial';font-size: 12px;color: black;">%s</td></tr>
                                        """ % (invoice.number, date_state, invoice.cfdi_uuid, invoice.partner_id.name, line_invoice.product_id.default_code, line_invoice.product_id.name, descargue.product_id.default_code, descargue.product_id.name, descargue.product_id.uom_id.name, descargue.quantity, line_descargue.partida_id.descripcion, line_descargue.partida_id.pedimento_num, line_descargue.partida_id.secuencia_fraccion, line_descargue.partida_id.fraccion_arancelaria, clave_documento.clave_documento, line_descargue.partida_id.cantidad_udm_comercial, line_descargue.quantity, line_descargue.partida_id.amount, factor, line_descargue.partida_id.udm_tarifa, line_descargue.partida_id.udm_comercial, uom_tarifa.name, uom_comercial.name)
        mail_obj = self.env['mail.mail']
        body_mail = u"""
                        <div summary="o_mail_notification" style="padding:0px; width:100%%;
                             margin:0 auto; background: #FFFFFF repeat top /100%%; color:#77777
                             7">
                                <table cellspacing="0" cellpadding="0" style="width:100%%;
                                border-collapse:collapse; background:inherit; color:inherit">
                                    <tbody><tr>
                                        <td align="left" width="270" style="padding:5px 10px
                                         5px 5px;font-size: 15px; font-family:'Arial'">
                                            <p class="titulo" style="font-family:'Arial';color: black;font-size: 18px;font-weight: 600;">Facturas RT</p>
                                        </td>
                                        <td align="right" width="310"
                                        style="padding:5px 15px 5px 10px; font-size: 12px; font-family:'Arial'">
                                            <p class="sent" style="font-family:'Arial';font-size: 14px;">
                                            <strong>Sent by</strong>
                                            <a href="http://erp.portalgebesa.com" style="text-
                                            decoration:none; color: #a24689;">
                                                <strong>%s</strong>
                                            </a>
                                            <strong>using</strong>
                                            <a href="https://www.odoo.com" style="text-
                                            decoration:none; color: #a24689;"><strong>Odoo
                                            </strong></a>
                                            </p>
                                        </td>
                                    </tr>
                                </tbody></table>
                            </div>
                            <div align="center" width:100%%; style="padding-top:5%%;">
                                <table>
                                    <tr>
                                        <td>
                                            <span style="font-family:'Arial';color: black;font-size: 16px; font-weight: bold;">Facturas de Exportacion con Material de Retorno del dia de ayer</span>
                                        </td>
                                    </tr>
                                </table>
                            </div>
                            <div style="padding:0px; width:100%%; margin:0 auto; background:
                            #FFFFFF repeat top /100%%; color:#777777">
                                <table cellspacing="0" cellpadding="0" style="vertical-align:
                                top; padding:0px; border-collapse:collapse; background:inherit;
                                 color:inherit; width:100%%;">
                                    <tbody><tr>
                                        <td valign="top" style="width:700px; padding:5px 10px
                                        5px 5px; ">
                                            <div>
                                                <hr width="100%%" style="background-color:
                                                rgb(204,204,204); border:medium none;clear:both;
                                                display:block;font-size:0px;min-height:1px;
                                                line-height:0;margin:15px auto;padding:0">
                                            </div>
                                        </td>
                                    </tr></tbody>
                                </table>
                            </div>
                            <div style="padding:0px; width:100%%; margin:0 auto; background:
                            #FFFFFF repeat top /100%%;color:#777777">
                                <table style="border-collapse:collapse; margin: 0 auto; width: 100%%;">
                                    <tbody><tr>
                                        <th width="10%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Factura</strong></th>
                                        <th width="6%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Estado</strong></th>
                                        <th width="20%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Folio Fiscal</strong></th>
                                        <th width="15%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Cliente</strong></th>
                                        <th width="8%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Clave PT</strong></th>
                                        <th width="20%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Producto PT</strong></th>
                                        <th width="8%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Clave MP</strong></th>
                                        <th width="18%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Producto MP</strong></th>
                                        <th width="20%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>UDM MP</strong></th>
                                        <th width="7%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Cantidad MP</strong></th>
                                        <th width="10%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Partida</strong></th>
                                        <th width="12%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Num Pedimento</strong></th>
                                        <th width="10%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Secuencia Fraccion</strong></th>
                                        <th width="10%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Fraccion Arancelaria</strong></th>
                                        <th width="8%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Clave de Documento</strong></th>
                                        <th width="8%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Cantidad UMC original</strong></th>
                                        <th width="7%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Cantidad Descarga</strong></th>
                                        <th width="10%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Saldo</strong></th>
                                        <th width="10%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Factor</strong>
                                        <th width="10%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Clave UMT(partida)</strong></th>
                                        <th width="10%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Clave UMC(partida)</strong></th>
                                        <th width="10%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Clave UMT</strong></th>
                                        <th width="10%%" style="border-bottom: 1px solid silver;font-size: 14px;font-family:'Arial';color: white;text-align: center;background-color: #a24689;"><strong>Clave UMC</strong></th>
                                    </tr>
                                    %s
                                    </tbody>
                                </table>
                            </div>
                        """ % (self.env.user.company_id.name, table)
        destinatarios = self.env['ir.config_parameter'].sudo().get_param('immex_gebesa.receivers_email', 'False')
        mail = mail_obj.create({
            'subject': 'Facturas RT del dia de ayer',
            # 'email_to': 'cesar.barron@gebesa.com,alejandra.caballero@gebesa.com,cristina.rodriguez@gebesa.com,customerservice@dura-box.com,sebastian@gebesa.com,brenda.hernandez@gebesa.com',
            'email_to': destinatarios,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def create(self, vals_list):
        if 'immex_not_invoce' in vals_list and vals_list['immex_not_invoce'] == True:
            return self
        return super().create(vals_list)
