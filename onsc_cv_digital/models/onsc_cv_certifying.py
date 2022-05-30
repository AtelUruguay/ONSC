# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVCertifyingInstitution(models.Model):
    _name = 'onsc.cv.certifying.institution'
    _description = 'Institución certificadora'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char(u'Nombre de la Institución certificadora', required=True)
    institution_id = fields.Many2one('onsc.cv.institution', string=u'Institución', required=True)
    subinstitution_cert_ids = fields.One2many('onsc.cv.certifying.subinstitution',
                                              inverse_name='institution_cert_id',
                                              string='Subinstituciones certificadoras',
                                              required=False)


class ONSCCVCertifyingSubinstitution(models.Model):
    _name = 'onsc.cv.certifying.subinstitution'
    _description = 'Sub institución certificadora'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char(u'Nombre de la Sub institución certificadora', required=True)
    institution_cert_id = fields.Many2one('onsc.cv.certifying.institution', string=u'Sub institución', required=True)
