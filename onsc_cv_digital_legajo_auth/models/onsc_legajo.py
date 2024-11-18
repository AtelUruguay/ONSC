# -*- coding: utf-8 -*-

from odoo.addons.onsc_base.onsc_useful_tools import to_timestamp as to_timestamp

from odoo import models, fields, _


class ONSCLegajo(models.Model):
    _inherit = "onsc.legajo"

    def button_actualizar_dnic(self):
        self.suspend_security().with_context(ignore_restrict=True).cv_digital_id.button_actualizar_dnic()
        return True
