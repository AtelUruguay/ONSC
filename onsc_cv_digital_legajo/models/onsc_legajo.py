# -*- coding: utf-8 -*-

from odoo import models, fields


class ONSCLegajo(models.Model):
    _inherit = "onsc.legajo"

    cv_digital_id = fields.Many2one(
        comodel_name="onsc.cv.digital",
        related='employee_id.cv_digital_id', store=True)

    # FORMACION
    basic_formation_ids = fields.One2many(
        'onsc.cv.basic.formation', string=u'Formación básica',
        domain="[('documentary_validation_state','=','validated')]",
        related='cv_digital_id.basic_formation_ids')
    advanced_formation_ids = fields.One2many(
        'onsc.cv.advanced.formation', string=u'Formación avanzada',
        domain="[('documentary_validation_state','=','validated')]",
        related='cv_digital_id.advanced_formation_ids')
