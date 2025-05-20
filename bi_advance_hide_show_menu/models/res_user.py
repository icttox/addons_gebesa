# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import operator
import logging
from odoo import models, fields, api, tools
# from odoo.tools.safe_eval import safe_eval
from odoo.http import request
from odoo.exceptions import AccessDenied
from decorator import decorator
_logger = logging.getLogger(__name__)


def assert_log_admin_access(method):
    """Decorator checking that the calling user is an administrator, and logging the call.

    Raises an AccessDenied error if the user does not have administrator privileges, according
    to `user._is_admin()`.
    """
    def check_and_log(method, self, *args, **kwargs):
        user = self.env.user
        origin = request.httprequest.remote_addr if request else 'n/a'
        log_data = (method.__name__, self.sudo().mapped('name'), user.login, user.id, origin)
        if not self.env.user._is_admin():
            _logger.warning('DENY access to module.%s on %s to user %s ID #%s via %s', *log_data)
            raise AccessDenied()
        _logger.info('ALLOW access to module.%s on %s to user %s #%s via %s', *log_data)
        return method(self, *args, **kwargs)
    return decorator(check_and_log, method)


class Module(models.Model):
    _inherit = "ir.module.module"

    @assert_log_admin_access
    @api.multi
    def button_immediate_install(self):
        menus_obj = self.env['ir.ui.menu'].search([], order="id desc", limit=1)
        menus_obj.write({'is_write': True})
        """Installs the selected module(s) immediately and fully,
        returns the next res.config action to execute

        :returns: next res.config item to execute
        :rtype: dict[str, object]
        """
        _logger.info('User #%d triggered module installation', self.env.uid)
        return self._button_immediate_function(type(self).button_install)


class ResUsers(models.Model):
    _inherit = 'res.users'
    _description = 'Res Users'

    menu_access_ids = fields.Many2many('ir.ui.menu', string='Groups')

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        request.env['ir.ui.menu'].load_menus(request.debug)
        return res


class ResGroups(models.Model):
    _inherit = 'res.groups'
    _description = 'Res Groups'

    menu_ids = fields.Many2many('ir.ui.menu', string='Groups')


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"
    _description = 'Ir Ui Menu'

    is_write = fields.Boolean('Write', default=False)

    @api.model
    @api.returns('self')
    def get_user_roots_menu(self):
        # Regresa una lista de ids con los menus restringidos por grupo
        # del usuario actual
        menus_list = self.env.user.groups_id.mapped('menu_ids').mapped('id')

        # Busca todos los menus principales que no se esconda al usuario actual
        ir_ui_menu = self.search([
            ('id', 'not in', self.env.user.menu_access_ids.ids),
            ('parent_id', '=', False)])

        # Verifica si al usuario actual se le esconde menus por grupo
        if len(menus_list) > 0:
            # Busca los menus principales que el usuario no esten escondidos
            # por grupo de lista de menus que no se esconde al usuario
            ir_ui_menu = ir_ui_menu.search([
                ('id', 'in', ir_ui_menu.ids),
                ('id', 'not in', menus_list),
                ('parent_id', '=', False)])

        # Regresa los menus principales que no esten escondido usuario actual
        return ir_ui_menu

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        skip_update_pentaho = self._context.get('skip_update_pentaho', False)
        if not skip_update_pentaho and self.env.user.id != self.env.ref('base.user_root').id:
            request.env['ir.ui.menu'].load_menus(request.debug)
        return res

    @api.model
    @tools.ormcache_context('self._uid', 'debug', keys=('lang',))
    def load_menus(self, debug):
        # Busca el ultimo menú segun su id
        menus_obj = self.env['ir.ui.menu'].search(
            [], order="id desc", limit=1
        )
        # Si el menú encontrado tiene la bandera is_write establecido a falso...
        if menus_obj.is_write is False:
            # Metodo para ocultar reportes

            # hace una busqueda de todos los ir.ui.menu que no tengan un menú
            # padre al que el usuario actual tiene acceso
            # menu_acces_ids Many2many hacia ir.ui.menu
            user_hide = self.env['ir.ui.menu'].search([
                ('id', 'in', self.env.user.menu_access_ids.ids),
                ('parent_id', '=', False)
            ])

            # busca todos los grupos donde esté el usuario actual que no tengan
            # establecido algo en menu_ids
            res_group_menu = self.env['res.groups'].search([
                ('users', 'in', self.env.user.id),
                ('menu_ids', '!=', False)
            ])

            # Variable tipo deccionario con campos del modelo de menu
            data_fields = [
                'name', 'sequence', 'parent_id',
                'action', 'web_icon', 'web_icon_data']

            # verifica que el usuario actual tiene menu que esconder o tiene grupos asignados
            if user_hide or res_group_menu:
                # Regresa todos los menus padres que puede ver el usuario actual
                menu_roots = self.get_user_roots_menu()
            else:
                # Mismo proceso que los bloques anteriores pero sin filtrar menus
                menu_roots = self.get_user_roots()

            # Regresa un arreglo de diccionarios con los
            # campos enlistados en la variable data_fields
            menu_roots_data = menu_roots.read(data_fields) if menu_roots else []
            # Diccionario con menu ficcticio para regresar si no hay menus que ver
            menu_root = {
                'id': False,
                'name': 'root',
                'parent_id': [-1, ''],
                'children': menu_roots_data,
                'all_menu_ids': menu_roots.ids,
            }

            # verifica que tenga menus padres que ver
            if not menu_roots_data:
                # regresa un menu ficcticio sin datos
                return menu_root

            # menus are loaded fully unlike a regular tree view, cause there are a
            # limited number of items (752 when all 6.1 addons are installed)
            # Busca los sub menus de los menu principales que se puede ver
            child_menus = self.search([('id', 'child_of', menu_roots.ids)])
            # se quitan submenus que se esconden al usuario actual
            menus = child_menus.search([
                ('id', 'not in', self.env.user.menu_access_ids.ids)])
            # verifica si el usuario actual tiene grupos
            if res_group_menu:
                menu_list = res_group_menu.mapped('menu_ids').mapped('id')

                menus = child_menus.search([
                    ('id', 'not in', list(set(menu_list))),
                    ('id', 'not in', self.env.user.menu_access_ids.ids)])

            menu_items = menus.read(data_fields)
            # add roots at the end of the sequence, so that they will overwrite
            # equivalent menu items from full menu read when put into id:item
            # mapping, resulting in children being correctly set on the roots.
            menu_items.extend(menu_roots_data)
            menu_root['all_menu_ids'] = menus.ids  # includes menu_roots!

            # make a tree using parent_id
            menu_items_map = {
                menu_item["id"]: menu_item for menu_item in menu_items}
            for menu_item in menu_items:
                parent = menu_item['parent_id'] and menu_item['parent_id'][0]
                if parent in menu_items_map:
                    menu_items_map[parent].setdefault(
                        'children', []).append(menu_item)

            # sort by sequence a tree using parent_id
            for menu_item in menu_items:
                menu_item.setdefault('children', []).sort(
                    key=operator.itemgetter('sequence'))

            (menu_roots + menus)._set_menuitems_xmlids(menu_root)

            return menu_root

        menus_obj.write({'is_write': False})
        return super().load_menus(request.debug)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
