odoo.define('onsc_legajo.BasicView', function (require) {
"use strict";

var BasicView = require('web.BasicView');

BasicView.include({
    init: function (viewInfo, params) {
        this._super.apply(this, arguments);
        if (params.hasOwnProperty('action') && params.action.hasOwnProperty('xml_id') && params.action.xml_id.includes('legajo') && (viewInfo.base_model === "hr.contract" || viewInfo.base_model === "hr.employee" || viewInfo.base_model === "hr.job")){
            this.controllerParams.archiveEnabled = false
        }
    }
})
});