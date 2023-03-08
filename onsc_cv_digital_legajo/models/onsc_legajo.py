# -*- coding: utf-8 -*-

from odoo import models, fields


class ONSCLegajo(models.Model):
    _inherit = "onsc.legajo"

    cv_digital_id = fields.Many2one(
        comodel_name="onsc.cv.digital",
        related='employee_id.cv_digital_id', store=True)
