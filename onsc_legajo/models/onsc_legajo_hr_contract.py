# -*- coding:utf-8 -*-
import json

from odoo import fields, models, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora")
    operating_unit_id_domain = fields.Char(compute='_compute_operating_unit_id_domain')
    sec_position = fields.Char(string="Sec Plaza", required=True)

    @api.onchange('inciso_id')
    def onchange_inciso(self):
        self.operating_unit_id = False

    @api.onchange('employee_id', 'sec_position')
    def onchange_employee(self):
        if self.employee_id:
            name = self.employee_id.cv_nro_doc if self.employee_id.cv_nro_doc else ''
            if self.sec_position:
                name += ' - ' + self.sec_position if self.sec_position else ''
            self.name = name
        else:
            self.name = False

    @api.depends('date_start', 'date_end', 'inciso_id')
    def _compute_operating_unit_id_domain(self):
        for rec in self:
            if rec.inciso_id.id is False:
                self.operating_unit_id_domain = json.dumps([('id', 'in', [])])
            else:
                domain = [('inciso_id', '=', rec.inciso_id.id)]
                if rec.date_start:
                    domain = ['&'] + domain + [('start_date', '<=', fields.Date.to_string(rec.date_start))]
                if rec.date_end:
                    domain = ['&'] + domain + ['|', ('end_date', '>=', fields.Date.to_string(rec.date_end)),
                                               ('end_date', '=', False)]
                self.operating_unit_id_domain = json.dumps(domain)
