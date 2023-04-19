# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.osv import expression


class ONSCCVFileValidationConfig(models.Model):
    _inherit = 'onsc.cv.documentary.validation.config'

    type = fields.Selection(string="Tipo",
                            required=True,
                            default='both',
                            selection=[('cv_call', 'Llamado'), ('legajo', 'Legajo'), ('both', 'Ambos')])

    def get_config(self, name=False):
        if self._context.get('is_legajo', False):
            args = [('type', 'in', ['legajo', 'both'])]
        else:
            args = [('type', 'in', ['cv_call', 'both'])]

        if name:
            args = expression.AND([[('model_id.model', '=', name)], args])
        return self.search(args)
