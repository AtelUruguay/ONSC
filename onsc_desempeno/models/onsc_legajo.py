# -*- coding: utf-8 -*-

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ONSCLegajoScore(models.Model):
    _inherit = "onsc.legajo"

    def _is_group_legajo_hr_ue(self):
        return self.user_has_groups('onsc_legajo.group_legajo_hr_ue')

    def _is_group_legajo_hr_inciso(self):
        return self.user_has_groups('onsc_legajo.group_legajo_hr_inciso')

    def _is_group_legajo_consulta_legajos(self):
        return self.user_has_groups('onsc_legajo.group_legajo_consulta_legajos')

    def _is_group_legajo_admin_legajos(self):
        return self.user_has_groups('onsc_legajo.group_legajo_hr_admin')

    score_ids = fields.One2many('onsc.desempeno.score', compute='_compute_onsc_desempeno_score', string="Puntaje")
    show_alert = fields.Boolean("Tiene notificaciones pendientes?", compute='_compute_show_alert')
    notification_pending_text = fields.Text(
        compute=lambda s: s._get_value_config('notification_pending_text'),
        default=lambda s: s._get_value_config('notification_pending_text', True)
    )
    is_notification_pending_form_active = fields.Boolean(
        compute=lambda s: s._get_value_config('is_notification_pending_form_active'),
        default=lambda s: s._get_value_config('is_notification_pending_form_active', True)
    )

    def _compute_onsc_desempeno_score(self):
        Score = self.env['onsc.desempeno.score'].suspend_security()
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        for rec in self:
            try:
                args = []
                is_full_groups = self._is_group_legajo_consulta_legajos() or self._is_group_legajo_admin_legajos()
                if self._context.get('mi_legajo') or is_full_groups:
                    args = [('employee_id', '=', rec.employee_id.id),
                            ('is_employee_notified', '=', True),
                            ('is_pilot', '=', False), ('whitout_impact', '=', False)]
                else:
                    if self._is_group_legajo_hr_inciso():
                        args = [('inciso_id', '=', inciso_id), ('employee_id', '=', rec.employee_id.id),
                                ('is_employee_notified', '=', True),
                                ('is_pilot', '=', False), ('whitout_impact', '=', False)]
                    elif self._is_group_legajo_hr_ue():
                        args = [('operating_unit_id', '=', operating_unit_id), ('employee_id', '=', rec.employee_id.id),
                                ('is_employee_notified', '=', True),
                                ('is_pilot', '=', False), ('whitout_impact', '=', False)]
                if args:
                    rec.score_ids = Score.with_context(ignore_security_rules=True).search(args)
                else:
                    rec.score_ids = False
            except Exception as e:
                _logger.error(f"Error en el método de cálculo de score_ids: {e}")

    def _compute_show_alert(self):
        Score = self.env['onsc.desempeno.score'].suspend_security()
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        for rec in self:
            count_score = Score.with_context(ignore_security_rules=True).search_count(
                [('employee_id', '=', rec.employee_id.id), ('is_employee_notified', '=', False),
                 ('inciso_id', '=', inciso_id), ('operating_unit_id', '=', operating_unit_id),
                 ('evaluation_stage_id.closed_stage', '=', True)])
            if count_score > 0 and rec.is_notification_pending_form_active:
                rec.show_alert = True
            else:
                rec.show_alert = False

    def _get_value_config(self, help_field='', is_default=False):
        _url = eval('self.env.user.company_id.%s' % help_field)
        if is_default:
            return _url
        for rec in self:
            setattr(rec, help_field, _url)
