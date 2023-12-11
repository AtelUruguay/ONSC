# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCLegajoUpdateOccupationWizard(models.TransientModel):
    _name = 'onsc.confirm.wizard'
    _description = 'Wizard de confirmación genérico'

    message = fields.Char(string='Mensaje')

    def action_confirm(self):
        model_name = self._context.get('model_name', False)
        model_ids = self._context.get('model_ids', False) or self._context.get('active_ids', False)
        method_name = self._context.get('method_name', False)

        if not model_name or not model_ids or not method_name:
            return True

        model_recordset = self.env[model_name].browse(model_ids)

        if hasattr(model_recordset, method_name):
            toexecute = getattr(model_recordset, method_name)
            return toexecute()
        return True
