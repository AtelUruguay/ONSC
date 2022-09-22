# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCCVAbstractCommon(models.AbstractModel):
    _name = 'onsc.cv.abstract.common'
    _description = 'Modelo abstracto común para todas las entidades de CV(NO CV)'

    # CAMPOS PARA ALMACENAR EL ORIGEN EN LAS ENTIDADES DEL LLAMADO
    original_instance_identifier = fields.Integer(string="Id del documento origen en el CV")

    @api.returns(None, lambda value: value[0])
    def copy_data(self, default=None):
        res = super(ONSCCVAbstractCommon, self).copy_data(default=default)
        if hasattr(self, 'original_instance_identifier') and len(self) == 1:
            for data in res:
                data['original_instance_identifier'] = self.id
        return res


