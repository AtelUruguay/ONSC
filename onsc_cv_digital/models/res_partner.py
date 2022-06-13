# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

CV_SEX = [('male', 'Masculino'), ('feminine', 'Femenino')]

COLUMNS_FROZEN = [
    'name',
    'is_company',
    'image_1920',
    'cv_emissor_country_id',
    'cv_document_type_id',
    'cv_nro_doc',
    'cv_first_name',
    'cv_second_name',
    'cv_last_name_1',
    'cv_last_name_2',
    'cv_ci_name',
    'cv_ci_name_updated',
    'cv_birthdate',
    'cv_sex',
    'cv_last_name_adoptive_1',
    'cv_last_name_adoptive_2',
    'cv_name_adoptive',
    'cv_expiration_date',
    'is_partner_cv',
]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    cv_emissor_country_id = fields.Many2one('res.country', u'País emisor del documento')
    cv_document_type_id = fields.Many2one('onsc.cv.document.type', u'Tipo de documento')
    cv_nro_doc = fields.Char(u'Número de documento')
    cv_first_name = fields.Char(u'Primer nombre')
    cv_second_name = fields.Char(u'Segundo nombre')
    cv_last_name_1 = fields.Char(u'Primer apellido')
    cv_last_name_2 = fields.Char(u'Segundo apellido')
    cv_ci_name = fields.Char(u'Nombre en cédula')
    cv_ci_name_updated = fields.Char(u'Nombre en cédula actualizado')
    cv_birthdate = fields.Date(u'Fecha de nacimiento')
    cv_sex = fields.Selection(CV_SEX, u'Sexo')
    cv_last_name_adoptive_1 = fields.Char(u'Primer apellido adoptivo')
    cv_last_name_adoptive_2 = fields.Char(u'Segundo apellido adoptivo')
    cv_name_adoptive = fields.Char(u'Nombre adoptivo')
    cv_full_name_updated_date = fields.Date(u'Fecha de información nombre completo',
                                            compute='_compute_full_name_updated_date', store=True)
    cv_sex_updated_date = fields.Date(u'Fecha de información sexo', compute='_compute_cv_sex_updated_date')
    cv_expiration_date = fields.Date(u'Fecha de vencimiento documento de identidad')
    cv_photo_updated_date = fields.Date(u'Fecha de foto del/de la funcionario/a', compute='_compute_photo_updated_date')
    is_partner_cv = fields.Boolean(u'¿Es un contacto de CV?')
    is_cv_uruguay = fields.Boolean('¿Es documento uruguayo?', compute='_compute_is_cv_uruguay')

    _sql_constraints = [
        ('country_doc_type_nro_doc_uniq', 'unique(cv_emissor_country_id, cv_document_type_id, cv_nro_doc)',
         u'La combinación: País emisor del documento, tipo de documento y número de documento debe ser única'),
    ]

    @api.depends('cv_emissor_country_id')
    def _compute_is_cv_uruguay(self):
        for record in self:
            record.is_cv_uruguay = record.cv_emissor_country_id.code == 'UY'

    @api.depends('cv_first_name', 'cv_last_name_1', 'cv_last_name_2')
    def _compute_full_name_updated_date(self):
        for record in self:
            record.cv_full_name_updated_date = fields.Date.today()

    @api.depends('cv_sex')
    def _compute_cv_sex_updated_date(self):
        for record in self:
            record.cv_sex_updated_date = fields.Date.today()

    @api.depends('image_1920')
    def _compute_photo_updated_date(self):
        for record in self:
            record.cv_photo_updated_date = fields.Date.today()

    def check_can_update(self):
        """ Para actualizar los partner que tienen is_partner_cv en True
        se debe pasar por contexto can_update_contact_cv=True
        :return:
        """
        context = self._context or {}
        if not context.get('can_update_contact_cv') and 'install_xmlid' not in context:
            return len(self.filtered(lambda x: x.is_partner_cv)) == 0
        return True

    def write(self, values):
        if set([x for x in values]).intersection(set(COLUMNS_FROZEN)) and not self.check_can_update():
            raise ValidationError(_('No puede modificar un Contacto de ONSC'))
        return super(ResPartner, self).write(values)

    def unlink(self):
        if not self.check_can_update():
            return super(ResPartner, self).unlink()
        raise ValidationError(_('No puede eliminar un Contacto de ONSC'))
