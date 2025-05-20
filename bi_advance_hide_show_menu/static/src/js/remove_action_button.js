odoo.define('bi_advance_hide_show_menu.remove_export_option', function (require) {
"use strict";

var Sidebar = require('web.Sidebar');
var core = require('web.core');
var _t = core._t;
var _lt = core._lt;
    Sidebar.include({
        start: function () {
            var self = this;
            var def_export;
            var def_delete;
            var def_duplicate;
            var def_action;
            var def_print;
            var export_label = _t("Export");
            var delete_label = _t("Delete");
            var duplicate_label = _t("Duplicate");
            var action_label = _t("Action");
            var print_label = _t("Print");

            def_export = this.getSession().user_has_group('bi_advance_hide_show_menu.group_hide_export_action').then(function(has_group) {
                if (has_group)
                {
                    self.items['other'] = $.grep(self.items['other'], function(i){
                        return i && i.label && i.label != export_label;
                    });
                }
            });

            def_delete = this.getSession().user_has_group('bi_advance_hide_show_menu.group_hide_delete_action').then(function(has_group) {
                if (has_group)
                {   
                    self.items['other'] = $.grep(self.items['other'], function(i){
                        return i && i.label && i.label != delete_label;
                    });
                }
            });

            def_duplicate = this.getSession().user_has_group('bi_advance_hide_show_menu.group_hide_duplicate_action').then(function(has_group) {
                if (has_group)
                {
                    self.items['other'] = $.grep(self.items['other'], function(i){
                        return i && i.label && i.label != duplicate_label;
                    });
                }
            });


            def_action = this.getSession().user_has_group('bi_advance_hide_show_menu.group_hide_action_btn').then(function(has_group) {
                if (has_group)
                {   
                    self.sections = $.grep(self.sections, function(i){
                        if (i.label == action_label){
                            return i.label != action_label;
                        }
                        else{
                            return i.label = print_label;
                        }
                    });
                }
            });

            def_print = this.getSession().user_has_group('bi_advance_hide_show_menu.group_hide_print_btn').then(function(has_group) {
                if (has_group)
                {   
                    self.sections = $.grep(self.sections, function(i){
                        if (i.label == print_label){
                            return i.label != print_label;
                        }
                        else{
                            return i.label = action_label;
                        }
                    });
                }
            });
            return $.when(
            this._super.apply(this, arguments),
            def_export, def_delete, def_duplicate,def_action,def_print
        );
        },
    });
});
