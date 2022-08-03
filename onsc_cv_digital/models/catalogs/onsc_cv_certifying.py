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


class ONSCCVCertifyingSubinstitution(models.Model):
    _name = 'onsc.cv.certifying.subinstitution'
    _description = 'Sub institución certificadora'
    _inherit = ['onsc.cv.abstract.config']
    _fields_2check_unicity = ['name', 'institution_cert_id', 'state']

    name = fields.Char(u'Nombre de la sub institución certificadora', required=True)
    institution_cert_id = fields.Many2one('onsc.cv.certifying.institution',
                                          string=u'Institución certificadora',
                                          required=True)

    certificate_line_ids = fields.One2many(comodel_name="onsc.cv.certificate.line",
                                           inverse_name="subinstitution_cert_id",
                                           string="Lineas de certificados")

    def _check_validation_status(self):
        parent_states = self.mapped('institution_cert_id.state')
        if 'to_validate' in parent_states or 'rejected' in parent_states:
            raise ValidationError(_("No se puede una Sub institución certificadora si "
                                    "la Institución certificadora no está validada"))
        return super(ONSCCVCertifyingSubinstitution, self)._check_validation_status()

    def _get_conditional_unicity_message(self):
        return _("Ya existe un registro validado para %s, "
                 "Sub institución: %s" % (self.name, self.institution_cert_id.display_name))
