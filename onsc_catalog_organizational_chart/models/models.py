# -*- coding: utf-8 -*-

from odoo import models, fields


class Department(models.Model):
    _inherit = 'hr.department'
    _parent_store = True

    show_short_name = fields.Boolean(
        'Nombre Corto en Organigrama',
        history=True,
        tracking=True,
    )
    parent_path = fields.Char(index=True)

    history_name = fields.Char(compute='_compute_history_name')

    def _compute_history_name(self):
        as_of_date = self._context.get('as_of_date', fields.Date.today())
        for record in self:
            if record.show_short_name:
                custom_rec_name = 'short_name'
            else:
                custom_rec_name = 'name'
            record_withhistory = record.with_context(find_history=True, as_of_date=as_of_date,
                                                     custom_rec_name=custom_rec_name)
            if record_withhistory:
                record.history_name = record_withhistory.name_get()[0][1]
            else:
                record.history_name = record.name
