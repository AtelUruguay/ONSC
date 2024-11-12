# -*- coding: utf-8 -*-

from odoo.addons.onsc_base.onsc_useful_tools import to_timestamp as to_timestamp

from odoo import models, fields, _


class ONSCLegajo(models.Model):
    _inherit = "onsc.legajo"

    def button_actualizar_dnic(self):
        self.cv_digital_id.button_actualizar_dnic()
        self.cv_digital_id.cv_full_name = self.cv_digital_id.partner_id.cv_full_name
        self.cv_digital_id.cv_birthdate = self.cv_digital_id.partner_id.cv_birthdate
        self.employee_id.full_name = self.cv_digital_id.cv_full_name
        self.employee_id.cv_birthdate = self.cv_digital_id.partner_id.cv_birthdate
        self.employee_id.cv_sex = self.cv_digital_id.partner_id.cv_sex
        return True
