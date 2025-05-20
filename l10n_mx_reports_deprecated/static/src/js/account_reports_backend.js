odoo.define('l10n_mx_base.account_report_generic', function (require){
"use strict";

var core = require('web.core');
var Widget = require('web.Widget');
var formats = require('web.formats');
var Model = require('web.Model');
var time = require('web.time');
var ControlPanelMixin = require('web.ControlPanelMixin');
var ReportWidget = require('account_reports.ReportWidget');
var Dialog = require('web.Dialog');
var session = require('web.session');
var framework = require('web.framework');
var crash_manager = require('web.crash_manager');
var QWeb = core.qweb;
var _t = core._t;

var account_report_generic = require('account_reports.account_report_generic');

    account_report_generic.include({
        get_html: function() {
            var self = this;
            var defs = [];
            return new Model('account.report.context.common').call('return_context', [self.report_model, self.given_context, self.report_id]).then(function (result) {
                self.context_model = new Model(result[0]);
                self.context_id = result[1];
                // Finally, actually get the html and various data
                return self.context_model.call('get_html_and_data', [self.context_id, self.given_context], {context: session.user_context}).then(function (result) {
                    self.report_type = result.report_type;
                    self.html = result.html;
                    self.xml_export = result.xml_export;
                    // Add txt_export button
                    self.txt_export = result.txt_export;
                    self.fy = result.fy;
                    self.report_context = result.report_context;
                    self.report_context.available_companies = result.available_companies;
                    if (result.available_journals) {
                        self.report_context.available_journals = result.available_journals;
                    }
                    self.render_buttons();
                    self.render_searchview_buttons();
                    self.render_searchview();
                    self.render_pager();
                    defs.push(self.update_cp());
                    return $.when.apply($, defs);
                });
            });
        },
        render_buttons: function(){
            this._super();
            var self = this;
            this.$buttons = this._super();
            if (self.txt_export){
                this.$buttons.siblings('.o_account-widget-txt').removeClass('hide');
            };
            this.$buttons.siblings('.o_account-widget-txt').bind('click', function () {
                // For xml exports, first check if the export can be done
                return new Model('account.financial.html.report.xml.export').call('check', [self.report_model, self.report_id]).then(function (check) {
                    if (check === true) {
                        var myresult = new Model('account.financial.html.report.xml.export').call('check_data_report', [self.context_id]).then(function (dict_check) {
                            if (dict_check === false) {
                                framework.blockUI();
                                session.get_file({
                                    url: self.controller_url.replace('output_format', 'txt'),
                                    complete: framework.unblockUI,
                                    error: crash_manager.rpc_error.bind(crash_manager),
                                });
                            } else {
                                if (dict_check.name === 'partner') {
                                    dict_check.name = _t('Moves without supplier');
                                } else if (dict_check.name === 'partner_data'){
                                    dict_check.name = _t('Suppliers without information necessary for DIOT');
                                }
                                return self.do_action(dict_check);
                            }
                        });
                    } else {
                        // If it can't be done, show why.
                        Dialog.alert(this, check, {});
                    }
                });
            });
            return this.$buttons;
        }
    });

});
