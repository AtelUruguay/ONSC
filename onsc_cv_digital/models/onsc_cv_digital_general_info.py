# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVDigitalDriversLicense(models.Model):
    _name = 'onsc.cv.digital.drivers.license'
    _description = 'Licencia de Conducir'

    validade_date_divers_license = fields.Date("Fecha de vencimiento", required=True)
    category_drivers_license_id = fields.Many2one("onsc.cv.drivers.license.categories", "Categoría", required=True)
    digital_document_drivers_license = fields.Binary("Documento digitalizado licencia de conducir", required=True)
    cv_digital_id = fields.Many2one(comodel_name="onsc.cv.digital", string="CV")
    digital_document_drivers_license_attachment_id = fields.Many2one(comodel_name="ir.attachment",
                                                                     string="Documento digitalizado licencia de conducir Ajunto",
                                                                     compute="_compute_digital_documents")

    def _compute_digital_documents(self):
        for rec in self:
            rec.digital_document_civical_credential_attachment_id = self.env['ir.attachment'].search(
                [('res_model', '=', 'onsc.cv.digital.drivers.license'), ('res_id', '=', rec.id),
                 ('res_field', '=', 'digital_document_drivers_license')])
