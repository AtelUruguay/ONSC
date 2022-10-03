odoo.define('onsc_cv_digital.FormRenderer', function (require) {
"use strict";
var FormRenderer = require('web.FormRenderer');

    FormRenderer.include({
        _renderTagLabel: function (node) {
//          # pylint: disable=javascript-lint
            let result = this._super.apply(this, arguments);
            if(node.attrs['doc-validation']){
                result.addClass('text-muted')
            }
            return result;
        }
    })
});
