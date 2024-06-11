# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCLegajoReportWizard(models.TransientModel):
    _name = 'onsc.legajo.report.wizard'
    _description = 'Reporte de Legajo'

    seccion_ids = fields.Many2many("onsc.legajo.report.config.seccion",
                                   string="Secciones",
                                   default=lambda self: self._get_default_seccion_ids())

    @api.model
    def _get_default_seccion_ids(self):
        return self.env['onsc.legajo.report.config.seccion'].search([('is_default', '=', True)]).ids

    def get_seccions(self):
        seccion_data = []
        for seccion in self.seccion_ids:
            seccion_data.append(seccion.internal_field)
        return seccion_data

    def button_print(self):
        active_ids = self._context.get('active_ids', False)
        legajo_ids = self.env['onsc.legajo'].browse(active_ids)
        if len(legajo_ids) == 0:
            return True
        action_report = self.env.ref('onsc_cv_digital_legajo.action_report_onsc_legajo')
        _ctx = self._context.copy()
        _ctx['seccions'] = self.get_seccions()
        action_report.suspend_security().context = _ctx
        res = action_report.report_action(legajo_ids)
        res.update({'close_on_report_download': True})
        return res
