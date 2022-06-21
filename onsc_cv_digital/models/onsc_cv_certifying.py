# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class ONSCCVCertifyingInstitution(models.Model):
    _name = 'onsc.cv.certifying.institution'
    _description = 'Institución certificadora'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char(u'Nombre de la institución certificadora', required=True)
    subinstitution_cert_ids = fields.One2many('onsc.cv.certifying.subinstitution',
                                              inverse_name='institution_cert_id',
                                              string='Sub instituciones certificadoras')

    def _check_validate(self, args2validate, message=""):
        args2validate = [
            ('name', '=', self.name),
        ]
        return super(ONSCCVCertifyingInstitution, self)._check_validate(
            args2validate,
            _("Ya existe un registro validado para %s, Institución %s" % (
                self.name, self.institution_id.display_name))
        )


class ONSCCVCertifyingSubinstitution(models.Model):
    _name = 'onsc.cv.certifying.subinstitution'
    _description = 'Sub institución certificadora'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char(u'Nombre de la sub institución certificadora', required=True)
    institution_cert_id = fields.Many2one('onsc.cv.certifying.institution',
                                          string=u'Institución certificadora',
                                          required=True)

    def _check_validate(self, args2validate, message=""):
        if self.institution_cert_id.state != 'validated':
            raise ValidationError(_("La Institución certificadora no ha sido validada"))
        args2validate = [
            ('name', '=', self.name),
            ('institution_cert_id', '=', self.institution_cert_id.id),
        ]
        return super(ONSCCVCertifyingSubinstitution, self)._check_validate(
            args2validate,
            _("Ya existe un registro validado para %s, Sub institución %s" % (
                self.name, self.institution_cert_id.display_name))
        )
