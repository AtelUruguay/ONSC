# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCCVReportWizard(models.TransientModel):
    _name = 'onsc.cv.report.wizard'
    _description = 'Reporte de CV'

    cv_digital_ids = fields.Many2many("onsc.cv.digital")
    seccion_ids = fields.Many2many("onsc.cv.report.config.seccion",
                                   string="Secciones",
                                   default=lambda self: self._get_default_seccion_ids())

    @api.model
    def _get_default_seccion_ids(self):
        return self.env['onsc.cv.report.config.seccion'].search([('is_default', '=', True)]).ids

    @api.onchange('is_all_seccions')
    def onchange_is_all_seccions(self):
        if self.is_all_seccions == False:
            self.seccion_ids = [
                (6, 0, self.env['onsc.cv.report.config.seccion'].search([('is_default', '=', True)]).ids)
            ]
        else:
            self.seccion_ids = [(5,)]

    def button_print(self):
        # TODO: Reporte de CV
        if self.cv_digital_ids:
            onsc_cv_digital_ids = self.cv_digital_ids
        else:
            active_ids = self._context.get('active_ids', False)
            onsc_cv_digital_ids = self.env['onsc.cv.digital'].browse(active_ids)
        if len(onsc_cv_digital_ids) == 0:
            return True
        seccion_data = []
        for seccion in self.seccion_ids:
            seccion_data.append(seccion.internal_field)
        action_report = self.env.ref('onsc_cv_digital.action_report_onsc_cv_digital')
        action_report.suspend_security().context = {'seccions': seccion_data}
        res = action_report.report_action(onsc_cv_digital_ids)
        res.update({'close_on_report_download': True})
        return res
