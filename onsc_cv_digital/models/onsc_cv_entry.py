# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ONSCCVEntry(models.Model):
    _name = 'onsc.cv.entry'
    _description = 'Rubro'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char("Nombre del rubro", required=True, tracking=True)

    def _check_validate(self, args2validate=[], message=""):
        args2validate = [
            ('name', '=', self.name),
        ]
        return super(ONSCCVEntry, self)._check_validate(
            args2validate,
            _("Ya existe un registro validado para %s" % (self.name))
        )
