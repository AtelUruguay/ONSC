# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import ValidationError

DOCUMENTARY_VALIDATION_STATES = [('to_validate', 'Para validar'),
                                 ('validated', 'Validado'),
                                 ('rejected', 'Rechazado')]


class ONSCCVAbstractFileValidation(models.AbstractModel):
    _name = 'onsc.cv.abstract.documentary.validation'
    _description = 'Modelo abstracto de validación documental'

    documentary_validation_state = fields.Selection(string="Estado de validación documental",
                                                    selection=DOCUMENTARY_VALIDATION_STATES,
                                                    default='to_validate',
                                                    tracking=True)

    def unlink(self):
        if self._check_todisable():
            return super(ONSCCVAbstractFileValidation, self).unlink()

    def _check_todisable(self):
        if not self._fields.get('cv_digital_id', False) or self.env[
            'onsc.cv.documentary.validation.config'].search_count([('model_id.model', '=', self._name)]) is False:
            return True
        for record in self:
            if record.documentary_validation_state == 'validated' and record._check_todisable_dynamic_fields():
                raise ValidationError(
                    _(u"No es posible eliminar el registro porque está en estado de validación documental: 'Validado' "
                      u"y tiene o tuvo vínculo con el estado"))
        return True

    def _check_todisable_dynamic_fields(self):
        return self.cv_digital_id._is_rve_link()
