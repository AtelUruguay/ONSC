# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class ONSCLegajoStagingWS7(models.Model):
    _inherit = 'onsc.legajo.staging.ws7'

    def _set_modif_funcionario_extras(self, contract, record):
        employee_id = contract.employee_id
        if not employee_id:
            raise ValidationError(_("No se pudo identificar el funcionario."))
        self._check_employee_valid_eff_date(employee_id, fields.Date.today())
        contract.legajo_id.cv_digital_id.suspend_security().with_context(no_post_history=True).write({
            'marital_status_id': record.marital_status_id.id,
            'marital_status_documentary_validation_state': 'validated',
            'marital_status_write_date': record.fecha_aud.date(),
            'marital_status_documentary_validation_date': record.fecha_aud.date(),
            'marital_status_documentary_user_id': self.create_uid.id,
        })
        employee_id.suspend_security().write({
            'eff_date': fields.Date.today(),
            'marital_status_id': record.marital_status_id.id
        })
        return True

    def _check_employee_valid_eff_date(self, employee_id, eff_date):
        if isinstance(eff_date, str):
            _eff_date = fields.Date.from_string(eff_date)
        else:
            _eff_date = eff_date
        if employee_id.eff_date and employee_id.eff_date > _eff_date:
            raise ValidationError(_("No se puede modificar la historia del funcionario para la fecha enviada."))
