odoo.define('rh_gebesa.UserMenu', function (require) {
    "use strict";

    /**
     * This file includes the UserMenu widget defined in Community to add or
     * override actions only available in Enterprise.
     */

    var config = require('web.config');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var UserMenu = require('web.UserMenu');
    var rpc = require('web.rpc');
    var _t = core._t;
    var QWeb = core.qweb;

    UserMenu.include({

        /**
         * @private
         */
        _onMenuHolidays: function() {
            var session = this.getSession();

            var employee = rpc.query({
                model: 'hr.employee',
                method: 'search_read',
                args: [[['user_id', '=', session.uid]]],
            }).then(function (employee) {
                new Dialog(this, {
                    size: 'medium',
                    dialogClass: 'o_act_window',
                    title: _t("Holidays"),
                    $content: $(QWeb.render(
                        "UserMenu.holidays",
                        {
                            'user_name': session.name,
                            'employee': employee[0],
                        }))
                }).open();                
            });

        },

    });

});
