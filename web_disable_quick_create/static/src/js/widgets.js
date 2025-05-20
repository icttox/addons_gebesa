odoo.define('disable_quick_create', function (require) {
    "use strict";

    var core = require('web.core');
    var fieldRegistry = require('web.field_registry');
    var FieldMany2One = fieldRegistry.get('many2one');
    var ListFieldMany2One = fieldRegistry.get('list.many2one');

    var fieldmany2one = FieldMany2One.extend({

        _search: function(search_val) {
                this.nodeOptions.no_create = true;
                this.nodeOptions.no_quick_create = true;
            return this._super(search_val);
            },

        });

    var listfieldmany2one = ListFieldMany2One.extend({
        
        init: function () {
            this._super.apply(this, arguments);
            this.nodeOptions.no_create = true;
            this.nodeOptions.no_quick_create = true;
            }
        });

     fieldRegistry.add('many2one', fieldmany2one);
     fieldRegistry.add('list.many2one', listfieldmany2one);
});
