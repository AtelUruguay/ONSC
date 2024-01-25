# -*- coding: utf-8 -*-

from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class ONSCLegajoScore(models.Model):
    _inherit = "onsc.legajo"

    score_ids = fields.One2many('onsc.desempeno.score', compute='_compute_onsc_desempeno_score', string="Puntaje")
    show_alert = fields.Boolean("Tiene notificaciones pendientes?")
    notification_pending_text = fields.Text(
        compute=lambda s: s._get_value_config('notification_pending_text'),
        default=lambda s: s._get_value_config('notification_pending_text', True)
    )


    def _compute_onsc_desempeno_score(self):
        Score = self.env['onsc.desempeno.score'].suspend_security()
        employee = self.env.user.employee_id
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        for rec in self:
            try:
                ids = Score.search([('employee_id', '=', employee.id), ('is_employee_notified', '=', True),
                                          ('inciso_id','=',inciso_id), ('operating_unit_id', '=', operating_unit_id)]).ids
                if ids:
                    rec.score_ids = ids
            except Exception as e:
                _logger.error(f"Error en el método de cálculo de score_ids: {e}")

    def _compute_show_alert(self):
        Score = self.env['onsc.desempeno.score'].suspend_security()
        employee = self.env.user.employee_id
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        count_score = Score.search_count([('employee_id', '=', employee.id), ('is_employee_notified', '=', False),
                                  ('inciso_id', '=', inciso_id), ('operating_unit_id', '=', operating_unit_id),
                                        ('evaluation_stage_id.closed_stage', '=', False)])
        if count_score > 0:
              self.show_alert = True

    def _get_value_config(self, help_field='', is_default=False):
        _url = eval('self.env.user.company_id.%s' % help_field)
        if is_default:
            return _url
        for rec in self:
            setattr(rec, help_field, _url)