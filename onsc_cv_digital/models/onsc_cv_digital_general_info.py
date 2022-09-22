# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVDigitalDriverLicense(models.Model):
    _name = 'onsc.cv.driver.license'
    _inherit = ['onsc.cv.abstract.documentary.validation']
    _description = 'Licencia de conducir'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", required=True, index=True, ondelete='cascade')
    validation_date = fields.Date("Fecha de vencimiento", required=True)
    category_id = fields.Many2one("onsc.cv.drivers.license.categories", "Categoría", required=True)
    license_file = fields.Binary("Documento digitalizado licencia de conducir", required=True)
    license_filename = fields.Char('Nombre del documento digital')
