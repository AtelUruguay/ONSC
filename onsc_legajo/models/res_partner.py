# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    legajo_employee_id = fields.Many2one("hr.employee", string="Empleado", compute="_compute_employee_id", store=True)

    @api.depends('cv_nro_doc')
    def _compute_employee_id(self):
        cv_emissor_country_id = self.env.ref('base.uy').id
        cv_document_type_id = self.env['onsc.cv.document.type'].sudo().search([('code', '=', 'ci')],
                                                                              limit=1).id or False
        for record in self:
            record.legajo_employee_id = self.env['hr.employee'].sudo().search([
                ('cv_emissor_country_id', '=', cv_emissor_country_id),
                ('cv_document_type_id', '=', cv_document_type_id),
                ('cv_nro_doc', '=', record.cv_nro_doc),
            ], limit=1)
