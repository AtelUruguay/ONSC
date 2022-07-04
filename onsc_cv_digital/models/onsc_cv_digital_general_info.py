# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCCVDigitalDriverLicense(models.Model):
    _name = 'onsc.cv.driver.license'
    _description = 'Licencia de conducir'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", index=True)
    validation_date = fields.Date("Fecha de vencimiento", required=True)
    category_id = fields.Many2one("onsc.cv.drivers.license.categories", "Categoría", required=True)
    license_file = fields.Binary("Documento digitalizado licencia de conducir", required=True)
    license_attachment_id = fields.Many2one("ir.attachment",
                                            string="Documento digitalizado licencia de conducir adjunto",
                                            compute="_compute_digital_documents", store=True)

    @api.depends('license_file')
    def _compute_digital_documents(self):
        Attachment = self.env['ir.attachment']
        for rec in self:
            rec.license_attachment_id = Attachment.search(
                [('res_model', '=', 'onsc.cv.driver.license'), ('res_id', '=', rec.id),
                 ('res_field', '=', 'license_file')], limit=1)
