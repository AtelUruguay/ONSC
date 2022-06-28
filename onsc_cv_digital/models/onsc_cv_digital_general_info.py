# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCCVDigitalDriverLicense(models.Model):
    _name = 'onsc.cv.digital.driver.license'
    _description = 'Licencia de Conducir'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", index=True)
    validation_date = fields.Date("Fecha de vencimiento", required=True)
    category_id = fields.Many2one("onsc.cv.drivers.license.categories", "Categoría", required=True)
    digital_document = fields.Binary("Documento digitalizado licencia de conducir", required=True)
    digital_document_attachment_id = fields.Many2one("ir.attachment",
                                                                    string="Documento digitalizado licencia de conducir adjunto",
                                                                    compute="_compute_digital_documents",store=True)
    @api.depends('digital_document')
    def _compute_digital_documents(self):
        attachment_object = self.env['ir.attachment']
        for rec in self:
            rec.digital_document_attachment_id = attachment_object.search(
                [('res_model', '=', 'onsc.cv.digital.driver.license'), ('res_id', '=', rec.id),
                 ('res_field', '=', 'digital_document')], limit=1)
