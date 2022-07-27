# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ONSCCVCertificate(models.Model):
    _name = 'onsc.cv.certificate'
    _description = 'Certificado'
    _inherit = ['onsc.cv.abstract.config']

    @api.model
    def default_get(self, fields):
        res = super(ONSCCVCertificate, self).default_get(fields)
        if self._context.get('default_institution_cert_id') and self._context.get('default_subinstitution_cert_id'):
            res['line_ids'] = [(0, 0, {
                'institution_cert_id': self._context.get('default_institution_cert_id'),
                'subinstitution_cert_id': self._context.get('default_subinstitution_cert_id'),
            })]
        return res

    name = fields.Char("Nombre del certificado", required=True, tracking=True)
    line_ids = fields.One2many('onsc.cv.certificate.line', inverse_name='certificate_id', string='Líneas',
                               required=True)

    @api.constrains('name', 'line_ids')
    def _check_valid_certificate(self):
        for record in self:
            if len(record.line_ids) == 0:
                raise ValidationError(_("Debe cargar al menos una Institución/Sub institución certificadora"))


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
        if (self.institution_cert_id and self.subinstitution_cert_id.institution_cert_id != self.institution_cert_id) \
                or self.institution_cert_id.id is False:
            self.subinstitution_cert_id = False
