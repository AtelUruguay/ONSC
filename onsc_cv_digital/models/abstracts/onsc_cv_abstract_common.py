# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ONSCCVAbstractCommon(models.AbstractModel):
    _name = 'onsc.cv.abstract.common'
    _description = 'Modelo abstracto común para todas las entidades de CV(NO CV)'

    # CAMPOS PARA ALMACENAR EL ORIGEN EN LAS ENTIDADES DEL LLAMADO
    original_instance_identifier = fields.Integer(string="Id del documento origen en el CV")

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = default or {}
        default['original_instance_identifier'] = self.id
        return super().copy(default=default)
