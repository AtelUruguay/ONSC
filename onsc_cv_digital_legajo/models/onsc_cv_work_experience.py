# -*- coding: utf-8 -*-
from odoo import fields, models


class ONSCCVDigitalWorkExperience(models.Model):
    _inherit = 'onsc.cv.work.experience'

    causes_discharge = fields.Char(string=u"Causal de egreso")
    causes_discharge_id = fields.Many2one("onsc.legajo.causes.discharge", string=u"Causal de egreso")

    def _get_json_dict(self):
        json_dict = super(ONSCCVDigitalWorkExperience, self)._get_json_dict()
        json_dict.extend([
            ("causes_discharge"),
        ])
        return json_dict

    def set_legajo_validated_records(self):
        LegajoModel = self.env['onsc.legajo.work.experience'].suspend_security()
        employee = self.cv_digital_id.employee_id
        legajo = self.env['onsc.legajo'].sudo().search([('employee_id', '=', employee.id)], limit=1)

        legajo_rec = self.copy_data(default={
            'employee_id': employee.id,
            'legajo_id': legajo.id,
            'origin_work_experience_id': self.id
        })
        new_legajo_record = LegajoModel.create(legajo_rec)
        return new_legajo_record
