# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ONSCCVTypeEvent(models.Model):
    _name = 'onsc.cv.type.event'
    _description = 'Tipo de Evento'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char(" Nombre del tipo de evento", required=True, tracking=True)

    def _check_validate(self, args2validate, message=""):
        args2validate = [
            ('name', '=', self.name),
        ]
        return super(ONSCCVTypeEvent, self)._check_validate(
            args2validate,
            _("Ya existe un registro validado para %s" % (self.name))
        )
