# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ONSCCVCertificate(models.Model):
    _name = 'onsc.cv.certificate'
    _description = 'Certificado'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char("Nombre del certificado", required=True, tracking=True)
    line_ids = fields.One2many('onsc.cv.certificate.line', inverse_name='certificate_id', string='Líneas',
                               required=True)

    @api.constrains('name', 'line_ids')
    def _check_valid_certificate(self):
        for record in self:
            if len(record.line_ids) == 0:
                raise ValidationError(_("Debe cargar al menos una Institución/Sub institución certificadora"))

    def _check_validate(self, args2validate, message=""):
        args2validate = [
            ('name', '=', self.name),
        ]
        return super(ONSCCVCertificate, self)._check_validate(
            args2validate,
            _("Ya existe un registro validado para %s" % (self.name))
        )


class ONSCCVCertificateLine(models.Model):
    _name = 'onsc.cv.certificate.line'
    _description = 'Líneas de certificado'

    certificate_id = fields.Many2one('onsc.cv.certificate', string='Certificado', required=True, ondelete='cascade')
    institution_cert_id = fields.Many2one('onsc.cv.certifying.institution', string=u'Institución certificadora',
                                          required=True, ondelete='cascade')
    subinstitution_cert_id = fields.Many2one('onsc.cv.certifying.subinstitution',
                                             string=u'Sub institución certificadora', required=True,
                                             domain="[('institution_cert_id', '=', institution_cert_id)]",
                                             ondelete='cascade')

    @api.onchange('institution_cert_id')
    def onchange_institution_cert_id(self):
        if self.institution_cert_id and self.subinstitution_cert_id and \
                self.subinstitution_cert_id.institution_cert_id != self.institution_cert_id:
            self.subinstitution_cert_id = False
