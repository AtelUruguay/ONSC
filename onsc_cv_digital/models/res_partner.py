# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID, models, fields, api, _
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
    'cv_birthdate',
    'cv_sex',
    'cv_expiration_date',
    'is_partner_cv',
    'cv_location_id',
    'cv_nro_door',
    'is_cv_bis',
    'cv_amplification',
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

    cv_birthdate = fields.Date(u'Fecha de nacimiento')
    cv_sex = fields.Selection(CV_SEX, u'Sexo')
    cv_full_name_updated_date = fields.Date(u'Fecha de información nombre completo',
                                            compute='_compute_cv_full_name', store=True)
    cv_sex_updated_date = fields.Date(u'Fecha de información sexo', compute='_compute_cv_sex_updated_date')
    cv_expiration_date = fields.Date(u'Fecha de vencimiento documento de identidad')
    cv_photo_updated_date = fields.Date(u'Fecha de foto del/de la funcionario/a', compute='_compute_photo_updated_date')
    is_partner_cv = fields.Boolean(u'¿Es un contacto de CV?')
    is_cv_uruguay = fields.Boolean('¿Es documento uruguayo?', compute='_compute_is_cv_uruguay')
    cv_full_name = fields.Char('Nombre', compute='_compute_cv_full_name', store=True)
    cv_location_id = fields.Many2one('onsc.cv.location', u'Localidad/Ciudad')
    cv_nro_door = fields.Char(u'Número')
    is_cv_bis = fields.Boolean(u'BIS')
    cv_apto = fields.Char(u'Apto')
    cv_street3 = fields.Char(u'Y calle')
    cv_amplification = fields.Text(u"Aclaraciones")
    cv_address_state = fields.Selection(related='cv_location_id.state', string="Estado condicional")

    _sql_constraints = [
        ('country_doc_type_nro_doc_uniq', 'unique(cv_emissor_country_id, cv_document_type_id, cv_nro_doc)',
         u'La combinación: País emisor del documento, tipo de documento y número de documento debe ser única'),
    ]

    @api.depends('cv_emissor_country_id')
    def _compute_is_cv_uruguay(self):
        for record in self:
            record.is_cv_uruguay = record.cv_emissor_country_id.code == 'UY'

    @api.depends('is_partner_cv', 'cv_first_name', 'cv_second_name', 'cv_last_name_1', 'cv_last_name_2',
                 )
    def _compute_cv_full_name(self):
        for record in self:
            record.cv_full_name_updated_date = fields.Date.today()
            if record.is_partner_cv:
                name_values = [record.cv_first_name,
                               record.cv_second_name,
                               record.cv_last_name_1,
                               record.cv_last_name_2]
                record.cv_full_name = ' '.join([x for x in name_values if x])
            else:
                record.cv_full_name = record.name

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
        :return: True si el usuario puede modificar/eliminar los registros
        """
        context = self._context or {}
        if not context.get(
                'can_update_contact_cv') and 'install_xmlid' not in context and not self.env.uid != SUPERUSER_ID:
            return len(self.filtered(lambda x: x.is_partner_cv)) == 0
        return True

    @api.model
    def create(self, values):
        # Si no se envía el nombre en los partner de tipo cv
        if 'name' not in values and values.get('is_partner_cv', False):
            values.update({'name': 'Temp'})

        res = super(ResPartner, self).create(values)
        # Actualizar el nombre en el registro con el campo calculado en caso que existan diferencias
        if res.cv_full_name and res.name != res.cv_full_name:
            res.name = res.cv_full_name
        return res

    @api.model
    def _get_frozen_columns(self):
        return COLUMNS_FROZEN

    def write(self, values):
        if set([x for x in values]).intersection(set(self._get_frozen_columns())) and not self.check_can_update():
            raise ValidationError(_('No puede modificar un Contacto de ONSC'))
        res = super(ResPartner, self).write(values)
        # Actualizar los nombres en los registros con el campo calculado en caso que existan diferencias
        for rec in self.filtered(lambda x: x.name != x.cv_full_name and x.cv_full_name):
            rec.name = rec.cv_full_name
        return res

    def unlink(self):
        if self.check_can_update():
            return super(ResPartner, self).unlink()
        raise ValidationError(_('No puede eliminar un Contacto de ONSC'))
