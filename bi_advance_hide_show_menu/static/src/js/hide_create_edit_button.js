odoo.define("bi_advance_hide_show_menu.HideCreateImportExportBtnList", function(require) {
    "use strict";

    var ListController = require('web.ListController');
    var session = require('web.session');

    ListController.include({
        
        willStart: function () {
            var self = this;
            var def_create = session.user_has_group('bi_advance_hide_show_menu.group_create_btn_access').then(function (has_create_group) {
                self.has_create_group = has_create_group;
            });
            var def_import = session.user_has_group('bi_advance_hide_show_menu.group_import_btn_access').then(function (has_import_group) {
                self.has_import_group = has_import_group;
            });
            return $.when(
            this._super.apply(this, arguments),
            def_create,def_import
        );
        },
        getSelectedRecords: function () {
            var self = this;
            if (this.has_create_group) {
                this.$buttons.find('.o_list_button_add').hide();
            }
            return _.map(this.selectedRecords, function (db_id) {
                return self.model.get(db_id, {raw: true});
            });
        },
    })
});

odoo.define("bi_advance_hide_show_menu.HideCreateEditBtnList", function(require) {
    "use strict";

    var FormController = require('web.FormController');
    var session = require('web.session');

    FormController.include({
        
        willStart: function () {
            var self = this;
            var def_create = session.user_has_group('bi_advance_hide_show_menu.group_create_btn_access').then(function (has_create_group) {
                self.has_create_group = has_create_group;
            });
            var def_edit = session.user_has_group('bi_advance_hide_show_menu.group_edit_form_btn_access').then(function (has_edit_group) {
                self.has_edit_group = has_edit_group;
            });
            return $.when(
            this._super.apply(this, arguments),
            def_create,def_edit
            );
        },
    })
});

odoo.define("bi_advance_hide_show_menu.HideCreateImportBtnKanban", function(require) {
    "use strict";

    var KanbanController = require('web.KanbanController');
    var session = require('web.session');

    KanbanController.include({
        
        willStart: function () {
            var self = this;
            var def_create = session.user_has_group('bi_advance_hide_show_menu.group_create_btn_access').then(function (has_create_group) {
                self.has_create_group = has_create_group;
            });
            var def_import = session.user_has_group('bi_advance_hide_show_menu.group_import_btn_access').then(function (has_import_group) {
                self.has_import_group = has_import_group;
            });
            return $.when(
            this._super.apply(this, arguments),
            def_create,def_import
            );
        },
    })
});
