# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCCVReportWizard(models.TransientModel):
    _name = 'onsc.cv.report.wizard'
    _description = 'Reporte de CV'

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
        active_ids = self._context.get('active_ids', False)
        if not active_ids:
            return True
        onsc_cv_digital_ids = self.env['onsc.cv.digital'].browse(active_ids)
        seccion_data = []
        for seccion in self.seccion_ids:
            seccion_data.append(seccion)

        res = self.env.ref('onsc_cv_digital.action_report_onsc_cv_digital').report_action(onsc_cv_digital_ids, )
        res.update({'close_on_report_download': True})
        return res
