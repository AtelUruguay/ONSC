# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCCVCertificate(models.Model):
    _name = 'onsc.cv.certificate'
    _description = 'Certificado'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char("Nombre del Certificado", required=True, tracking=True)
    line_ids = fields.One2many('onsc.cv.certificate.line', inverse_name='certificate_id', string='Líneas',
                               required=True)


class ONSCCVCertificateLine(models.Model):
    _name = 'onsc.cv.certificate.line'
    _description = 'Líneas de Certificado'

    certificate_id = fields.Many2one('onsc.cv.certificate', string='Certificado', required=True, ondelete='cascade')
    institution_id = fields.Many2one('onsc.cv.institution', string=u'Institución', required=True, ondelete='cascade')
    subinstitution_id = fields.Many2one('onsc.cv.subinstitution', string=u'Sub institución', required=True,
                                        ondelete='cascade')

    @api.onchange('institution_id')
    def onchange_institution_id(self):
        self.subinstitution_id = False

