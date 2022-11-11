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

odoo.define('onsc_cv_digital.BasicView', function (require) {
var BasicView = require('web.BasicView');
BasicView.include({

        init: function(viewInfo, params) {
            var self = this;
            this._super.apply(this, arguments);
            const models =  ['onsc.cv.digital','onsc.cv.digital.call'] ;
            if(models.includes(self.controllerParams.modelName))
            {
               self.controllerParams.archiveEnabled = 'False' in viewInfo.fields;
            }
        },
    });
});
