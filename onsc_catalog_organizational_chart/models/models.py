# -*- coding: utf-8 -*-

from odoo import models, fields


class Department(models.Model):
    _inherit = 'hr.department'

    show_short_name = fields.Boolean(
        'Nombre corto en organigrama'
    )

    history_name = fields.Char(compute = '_compute_history_name')

    def _compute_history_name(self):
        as_of_date = self._context.get('as_of_date', fields.Date.today())
        for record in self:
            record_withhistory = record.with_context(find_history=True, as_of_date=as_of_date)
            if record_withhistory:
                record.history_name = record_withhistory.name_get()[0][1]
            else:
                record.history_name = self.inciso_id.name
