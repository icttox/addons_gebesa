odoo.define('commissions.tree_view_buttons', function (require) {
    "use strict";

    var ListController = require('web.ListController');


    ListController.include({
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (!this.$buttons) {
                return;
            }
            this.$buttons.on('click', '.or_tree_view_button_hr_salary_asing',
                this.open_view_wizard_salary_assing.bind(this));
        },

        open_view_wizard_salary_assing: function () {
            var action = {
                type: 'ir.actions.act_window',
                res_model: 'wizard.salary.assingments.xls',
                view_mode: 'form',
                view_id:
                    'hr_salary_assignments.wizard_assingments_import_xls_view',
                views: [[false, 'form']],
                target: 'new',
                context: {},
            };
            this.do_action(action);
        },
    });
});
