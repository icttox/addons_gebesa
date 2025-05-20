# coding: utf-8
# ##########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
# ############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# #########################################################################

import logging
from lxml import etree, html
from odoo import models, api, _
_logger = logging.getLogger(__name__)


class MessagePostShowAll(models.Model):

    """With this object you can add an extensive log in your model like the
    traditional message log don't does
    You need do it the following way:
        _name = "account.invoice"
        _inherit = ['account.invoice', 'message.post.show.all']

    """

    _name = 'message.post.show.all'
    _inherit = ['mail.thread']

    @api.model
    def text_from_html(self, html_content, max_words=None, max_chars=None,
                       ellipsis=u"…", fail=False):
        """Extract text from an HTML field in a generator.

        :param str html_content:
            HTML contents from where to extract the text.

        :param int max_words:
            Maximum amount of words allowed in the resulting string.

        :param int max_chars:
            Maximum amount of characters allowed in the resulting string. If
            you apply this limit, beware that the last word could get cut in an
            unexpected place.

        :param str ellipsis:
            Character(s) to be appended to the end of the resulting string if
            it gets truncated after applying limits set in :param:`max_words`
            or :param:`max_chars`. If you want nothing applied, just set an
            empty string.

        :param bool fail:
            If ``True``, exceptions will be raised. Otherwise, an empty string
            will be returned on failure.
        """
        # Parse HTML
        try:
            doc = html.fromstring(html_content)
        except (TypeError, etree.XMLSyntaxError, etree.ParserError):
            if fail:
                raise
            else:
                _logger.exception("Failure parsing this HTML:\n%s",
                                  html_content)
                return ""

        # Get words
        words = u"".join(doc.xpath("//text()")).split()

        # Truncate words
        suffix = max_words and len(words) > max_words
        if max_words:
            words = words[:max_words]

        # Get text
        text = u" ".join(words)

        # Truncate text
        suffix = suffix or max_chars and len(text) > max_chars
        if max_chars:
            text = text[:max_chars - (len(ellipsis) if suffix else 0)].strip()

        # Append ellipsis if needed
        if suffix:
            text += ellipsis

        return text

    # pylint: disable=W0622
    @api.model
    def get_last_value(self, ids, model=None, field=None,
                       fieldtype=None):
        """Return the last value of a record in the model to show a post with the
        change
        @param ids: int with id record
        @param model: String with model name
        @param field: Name field to return his value

        return the value of the field
        """

        field = ids and field or []
        model_obj = self.env[model]
        model_brw = model_obj.browse(ids)
        if 'many2one' in fieldtype:
            value = field and model_brw[field] and \
                model_brw[field].name_get() or ''
            value = value and value[0][1]
        elif 'many2many' in fieldtype:
            value = [i.id for i in model_brw[field]]
        else:
            value = field and model_brw[field] or ''

        return field and value or ''

    @api.model
    def prepare_many_info(self, ids, records, string, n_obj,
                          last=None):
        if not records:
            return ''
        info = {
            0: _('Created New Line'),
            1: _('Updated Line'),
            2: _('Removed Line'),
            3: _('Removed Line'),
            4: _('Add New Line'),
            6: _('many2many'),
        }

        message = '<ul>'
        obj = self.env[n_obj]
        r_name = obj._rec_name
        mes = ''
        last = last or []
        for val in records:
            if val and info.get(val[0], False):
                if val[0] == 0:
                    value = val[2]
                    message = '%s\n<li><b>%s<b>: %s</li>' % \
                        (message, info.get(val[0]),
                         value.get(r_name))
                elif val[0] in (2, 3, 4):
                    if val[0] == 4 and val[1] in last:
                        continue
                    model_brw = obj.browse(val[1])
                    last_value = model_brw.name_get()
                    last_value = last_value and last_value[0][1]
                    value = val[1]
                    message = '%s\n<li><b>%s<b>: %s</li>' % \
                        (message, info.get(val[0]),
                         last_value)

                elif val[0] == 6:
                    lastv = list(set(val[2]) - set(last))
                    new = list(set(last) - set(val[2]))
                    if not lastv and not new:
                        return ''
                    add = _('Added')
                    delete = _('Deleted')
                    if lastv and not new:
                        dele = [obj.browse(i).name_get()[0][1]
                                for i in lastv]
                        mes = ' - '.join(dele)
                        message = '%s\n<li><b>%s %s<b>: %s</li>' % \
                            (message, add, string,
                             mes)
                    if not lastv and new:

                        dele = [obj.browse(i).name_get()[0][1] for i in new]
                        mes = '-'.join(dele)
                        message = '%s\n<li><b>%s %s<b>: %s</li>' % \
                            (message, delete, string,
                             mes)

                elif val[0] == 1:
                    vals = val[2]
                    id_line = 0
                    for field in vals:
                        if obj._fields[field].type in \
                                ('one2many', 'many2many'):
                            is_many = obj._fields[field].type == 'many2many'

                            last_value = is_many and self.get_last_value(
                                val[1], n_obj, field, 'many2many')
                            field_str = self.get_string_by_field(obj, field)
                            new_n_obj = obj._fields[field].comodel_name
                            mes = self.prepare_many_info(val[1],
                                                         vals[field],
                                                         field_str,
                                                         new_n_obj,
                                                         last_value)

                        elif obj._fields[field].type == 'many2one':
                            mes = self.prepare_many2one_info(val[1],
                                                             n_obj,
                                                             field,
                                                             vals)

                        elif 'many' not in obj._fields[field].type:
                            mes = self.prepare_simple_info(val[1],
                                                           n_obj, field,
                                                           vals)
                        if mes and mes != '<p>':
                            message = id_line != val[1] and \
                                _('%s\n<li><h3>Line %s</h3></li>' % (message, val[1])) \
                                or message
                            message = '%s\n<ul>%s</ul>' % \
                                (message,
                                 mes)
                            id_line = val[1]

        message = '%s\n</ul>' % message
        return message

    @api.model
    def get_selection_value(self, source_obj, field, value):
        """Get the string of a selection field using
        fields_get method to get the string

        @param source_obj: Model that contains the field
        @type source_obj: RecordSet
        @param field: Database name of the field
        @type field: str or unicode
        @param value: Database value used to find its the
                      string in the selection
        @type value: str or unicode

        @returns: String shown in the selection field
        @rtype: str
        """
        val = source_obj.fields_get([field])
        val = val and val.get(field, {})
        val = val and val.get('selection', ()) or ()
        val = [i[1] for i in val if value in i]
        val = val and val[0] or ''
        return val

    @api.model
    def get_string_by_field(self, source_obj, field):
        """Get the string of a field using fields_get method to
        get the string depending of the user lang

        @param source_obj: Model that contains the field
        @type source_obj: RecordSet
        @param field: Database name of the field
        @type field: str or unicode

        @returns: String of the field shown in the views
        @rtype: str
        """
        description = source_obj.fields_get([field])
        description = description and description.get(field, {})
        description = description and description.get('string', '') or ''
        return description

    @api.model
    def prepare_many2one_info(self, ids, n_obj, field, vals):
        obj = self.env[n_obj]
        message = '<p>'

        last_value = self.get_last_value(
            ids, obj._name, field, obj._fields[field].type)
        model_obj = self.env[obj._fields[field].comodel_name]
        if vals[field] != '':
            model_brw = model_obj.browse(int(vals[field]))
        else:
            model_brw = model_obj.browse()
        new_value = model_brw.name_get()
        new_value = new_value and new_value[0][1]

        if not (last_value == new_value) and any((new_value, last_value)):
            message = '<li><b>%s<b>: %s → %s</li>' % \
                (self.get_string_by_field(obj, field),
                 last_value, new_value)
        return message

    @staticmethod
    def get_encode_value(value):
        """Encode string values to avoid unicode errors
        @param value: Any object to try encode the value
        @type value: str bool date
        """
        val = value
        if isinstance(value, (str)):
            val = value.encode('utf-8', 'ignore')
        return val

    @api.model
    def prepare_simple_info(self, ids, n_obj, field,
                            vals):
        obj = self.env[n_obj]
        message = '<p>'
        last_value = self.get_last_value(
            ids, obj._name, field, obj._fields[field].type)

        last_value = obj._fields[field].type == 'selection' and \
            self.get_selection_value(obj, field, last_value) or last_value
        new_value = obj._fields[field].type == 'selection' and \
            self.get_selection_value(obj, field, vals[field]) or vals[field]

        if field in self._fields and self._fields[field].type == 'html':
            if not new_value:
                new_value = ''
            elif not isinstance(new_value, str):
                new_value = str(new_value)
            if not last_value:
                last_value = ''
            elif not isinstance(last_value, str):
                last_value = str(last_value)
            new_value = self.text_from_html(new_value.replace('&nbsp;', '\xa0'))
            last_value = self.text_from_html(last_value)

        message = ((last_value != new_value) and
                   any((last_value, vals[field]))) and \
            '<li><b>%s<b>: %s → %s</li>' % \
            (self.get_string_by_field(obj, field), last_value,
             new_value) or '<p>'
        return message

    # pylint: disable=W0106
    @api.multi
    def write(self, vals):
        for idx in self:
            body = '<ul>'
            message = ''
            for field in vals:
                if self._fields[field].type in ('one2many', 'many2many'):
                    # is_many = self._fields[field].type == 'many2many'

                    # last_value = is_many and self.get_last_value(
                    #     idx.id, self._name, field, 'many2many')
                    last_value = self.get_last_value(
                        idx.id, self._name, field, 'many2many')
                    field_str = self.get_string_by_field(self, field)
                    n_obj = self._fields[field].comodel_name
                    message = self.prepare_many_info(
                        idx.id, vals[field], field_str, n_obj,
                        last_value)
                    body = len(message.split('\n')) > 2 and '%s\n%s: %s' % (
                        body, field_str, message) or body

                elif self._fields[field].type == 'many2one':
                    message = self.prepare_many2one_info(idx.id,
                                                         self._name,
                                                         field,
                                                         vals)
                    body = '%s\n%s' % (body, message)

                elif 'many' not in self._fields[field].type:
                    message = self.prepare_simple_info(
                        idx.id, self._name, field, vals)
                    body = '%s\n%s' % (body, message)

            body = body and '%s\n</ul>' % body
            # if message == '<p>':
            #     message = False
            if body and self.text_from_html(body) != '':
                msg = _('Changes in Fields')
                ctx = self._context.copy()
                if 'mark_so_as_sent' in ctx:
                    ctx['mark_so_as_sent'] = False
                if 'mark_rfq_as_sent' in ctx:
                    ctx['mark_rfq_as_sent'] = False
                idx.with_context(ctx).message_post(body=(msg + body))
        res = super(MessagePostShowAll, self).write(vals)
        return res
