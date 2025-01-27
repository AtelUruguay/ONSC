# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError

from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as cv_warning

REQUIRED_FIELDS = [
    'country_id',
    'cv_address_state_id',
    'cv_nro_doc',
    'country_of_birth_id',
    'uy_citizenship',
]


class ONSCCVMinimal(models.Model):
    _name = 'onsc.cv.minimal'
    _inherit = [
        'onsc.cv.abstract.phone.validated',
        'mail.thread',
        'mail.activity.mixin'
    ]
    _description = 'CVD Mínimo'
    _rec_name = 'cv_nro_doc'

    @property
    def prefix_by_phones(self):
        res = super().prefix_by_phones
        return res + [('prefix_phone_id', 'personal_phone'), ('prefix_mobile_phone_id', 'mobile_phone')]

    def _default_cv_document_type_id(self):
        return self.env['onsc.cv.document.type'].search([('code', '=', 'ci')], limit=1)

    cv_emissor_country_id = fields.Many2one(
        'res.country', u'País emisor del documento',
        required=True,
        default=lambda self: self.env.ref('base.uy', raise_if_not_found=False)
    )
    cv_document_type_id = fields.Many2one(
        'onsc.cv.document.type', u'Tipo de documento',
        required=True,
        default=_default_cv_document_type_id
    )
    cv_nro_doc = fields.Char(u'Número de documento', required=True, size=8)
    state = fields.Selection(
        string='Estado',
        selection=[
            ('draft', 'Borrador'),
            ('confirm', 'Confirmado'),
        ],
        default='draft',
        tracking=True
    )

    country_of_birth_id = fields.Many2one("res.country", string="País de nacimiento", copy=False)
    uy_citizenship = fields.Selection(string="Ciudadanía uruguaya", copy=False,
                                      selection=[('legal', 'Legal'), ('natural', 'Natural'),
                                                 ('extranjero', 'Extranjero')])
    marital_status_id = fields.Many2one("onsc.cv.status.civil", string="Estado civil", copy=False)
    crendencial_serie = fields.Char(string="Serie de la credencial", size=3, copy=False)
    credential_number = fields.Char(string="Numero de la credencial", size=6, copy=False)

    prefix_phone_id = fields.Many2one('res.country.phone', 'Prefijo',
                                      default=lambda self: self.env['res.country.phone'].search(
                                          [('country_id.code', '=', 'UY')]))
    prefix_mobile_phone_id = fields.Many2one('res.country.phone', 'Prefijo del móvil',
                                             default=lambda self: self.env['res.country.phone'].search(
                                                 [('country_id.code', '=', 'UY')]))
    personal_phone = fields.Char(string="Teléfono particular")
    mobile_phone = fields.Char(string="Teléfono celular")
    email = fields.Char(string="Email", required=True)

    # Domicilio
    country_id = fields.Many2one('res.country', string="País")
    country_code = fields.Char("Código", related="country_id.code", readonly=True)
    cv_address_state_id = fields.Many2one('res.country.state', string="Departamento")
    cv_address_street = fields.Char("Calle(Extranjero)")
    cv_address_location_id = fields.Many2one('onsc.cv.location', string=u"Localidad/Ciudad")
    cv_address_street_id = fields.Many2one('onsc.cv.street', string="Calle (Nacional)", copy=False)
    cv_address_street2_id = fields.Many2one('onsc.cv.street', string="Entre calle", copy=False)
    cv_address_street3_id = fields.Many2one('onsc.cv.street', string=u'Y calle', copy=False)
    cv_address_nro_door = fields.Char('Número', size=5)
    cv_address_is_cv_bis = fields.Boolean("BIS")
    cv_address_apto = fields.Char(string="Apto", size=4)
    cv_address_zip = fields.Char('C.P', size=6)
    cv_address_place = fields.Text(string="Paraje", size=200)
    cv_address_block = fields.Char(string="Manzana", size=5)
    cv_address_sandlot = fields.Char(string="Solar", size=5)
    cv_address_amplification = fields.Text("Aclaraciones")

    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')
    partner_id = fields.Many2one('res.partner', string="Contacto", copy=False)
    cv_full_name = fields.Char('Nombre', related='partner_id.cv_full_name', store=True)


    @api.onchange('cv_nro_doc')
    def onchange_cv_nro_doc(self):
        if self.cv_nro_doc and not self.cv_nro_doc.isdigit():
            self.cv_nro_doc = ''.join(filter(str.isdigit, self.cv_nro_doc))
            return cv_warning(_("El número de documento no puede contener letras"))

    @api.onchange('country_id')
    def onchange_country_id(self):
        if self.cv_address_state_id.country_id.id != self.country_id.id:
            self.cv_address_state_id = False

    @api.onchange('cv_address_state_id')
    def onchange_cv_address_state_id(self):
        if self.cv_address_state_id:
            self.country_id = self.cv_address_state_id.country_id.id
        self.cv_address_location_id = False

    @api.constrains('personal_phone', 'mobile_phone')
    def _check_valid_phone(self):
        for record in self:
            if not self._context.get('is_migration') and not record.personal_phone and not record.mobile_phone:
                raise ValidationError(_("Necesitas al menos introducir la información de un teléfono"))

    @api.onchange('uy_citizenship')
    def onchange_uy_citizenship(self):
        if self.uy_citizenship == 'extranjero':
            self.crendencial_serie = False
            self.credential_number = False

    @api.onchange('crendencial_serie')
    def onchange_crendencial_serie(self):
        if self.crendencial_serie and not self.crendencial_serie.isalpha():
            self.crendencial_serie = ''
            return cv_warning(_("La serie de la credencial no puede contener números"))
        if self.crendencial_serie and not self.crendencial_serie.isupper():
            self.crendencial_serie = self.crendencial_serie.upper()

    @api.onchange('credential_number')
    def onchange_credential_number(self):
        if self.credential_number and not self.credential_number.isdigit():
            self.credential_number = ''.join(filter(str.isdigit, self.credential_number))
            return cv_warning(_("El número de la credencial no puede contener letras"))

    @api.onchange('cv_address_block', 'cv_address_sandlot')
    def onchange_block_sandlot(self):
        if self.cv_address_block and not self.cv_address_block.isdigit():
            self.cv_address_block = ''.join(filter(str.isdigit, self.cv_address_block))
            return cv_warning(_("Manzana no puden contener letras"))
        if self.cv_address_sandlot and not self.cv_address_sandlot.isdigit():
            self.cv_address_sandlot = ''.join(filter(str.isdigit, self.cv_address_sandlot))
            return cv_warning(_("El Solar no puede contener letras"))

    @api.onchange('cv_address_location_id')
    def onchange_location_id(self):
        self.cv_address_street_id = False
        self.cv_address_street2_id = False
        self.cv_address_street3_id = False
        self.cv_address_street = False
        self.cv_address_nro_door = False
        self.cv_address_is_cv_bis = False
        self.cv_address_apto = False
        self.cv_address_zip = False
        self.cv_address_place = False
        self.cv_address_block = False
        self.cv_address_sandlot = False
        self.cv_address_amplification = False

    @api.onchange('cv_address_zip')
    def onchange_cv_address_zip(self):
        if self.cv_address_zip and not (self.cv_address_zip.isnumeric()):
            self.cv_address_zip = ''.join(filter(str.isdigit, self.cv_address_zip))
            return cv_warning(_("El C.P no puede contener letras"))

    @api.depends('state')
    def _compute_should_disable_form_edit(self):
        for record in self:
            record.should_disable_form_edit = record.state != 'draft'

    def unlink(self):
        if self.filtered(lambda x: x.state != 'draft'):
            raise ValidationError(_("Solo se pueden eliminar transacciones en estado borrador"))
        return super(ONSCCVMinimal, self).unlink()

    def button_confirm(self):
        self._check_required_fields()
        self._check_exist_cv()
        for rec in self:
            partner = rec._get_partner()
            rec._create_cv(partner)
            rec.write({'state': 'confirm', 'partner_id': partner.id})

    def _check_exist_cv(self):
        CVDigital = self.env['onsc.cv.digital'].sudo()
        for rec in self:
            if CVDigital.search_count([
                ('cv_emissor_country_id', '=', rec.cv_emissor_country_id.id),
                ('cv_document_type_id', '=', rec.cv_document_type_id.id),
                ('cv_nro_doc', '=', rec.cv_nro_doc),
            ]):
                raise ValidationError(_("No es posible continuar, esta persona ya tiene un CV digital cargado en el sistema"))

    def _check_required_fields(self):
        for record in self:
            message = []
            for required_field in REQUIRED_FIELDS:
                if not eval('record.%s' % required_field):
                    message.append(record._fields[required_field].string)
            if message:
                fields_str = '\n'.join(message)
                message = 'Información faltante o no cumple validación:\n \n%s' % fields_str
                raise ValidationError(_(message))

    def _get_partner(self, ):
        Partner = self.env['res.partner'].suspend_security()
        partner = Partner.search([
            ('cv_nro_doc', '=', self.cv_nro_doc),
            ('cv_emissor_country_id', '=', self.cv_emissor_country_id.id),
            ('cv_document_type_id', '=', self.cv_document_type_id.id),
        ], limit=1)
        if not partner:
            data_partner = {
                'cv_emissor_country_id': self.cv_emissor_country_id.id,
                'cv_document_type_id': self.cv_document_type_id.id,
                'cv_nro_doc': self.cv_nro_doc,

                'country_id': self.country_id.id,
                'state_id': self.cv_address_state_id.id,
                'cv_location_id': self.cv_address_location_id.id,
                'street': self.cv_address_street_id.display_name,
                'street2': self.cv_address_street2_id.display_name,
                'cv_street3': self.cv_address_street3_id.display_name,
                'cv_nro_door': self.cv_address_nro_door,
                'is_cv_bis': self.cv_address_is_cv_bis,
                'cv_apto': self.cv_address_apto,
                'cv_address_place': self.cv_address_place,
                'cv_address_block': self.cv_address_block,
                'cv_address_sandlot': self.cv_address_sandlot,
                'zip': self.cv_address_zip,

                'email': self.email,
                # 'cv_dnic_name_1': self.first_name,
                # 'cv_dnic_name_2': self.second_name,
                # 'cv_dnic_lastname_1': self.first_surname,
                # 'cv_dnic_lastname_2': self.second_surname,
                # 'cv_dnic_full_name': self.name_ci,
                # 'cv_birthdate': self.birth_date,
                # 'cv_first_name': self.first_name,
                # 'cv_second_name': self.second_name,
                # 'cv_last_name_1': self.first_surname,
                # 'cv_last_name_2': self.second_surname,
                'is_partner_cv': True,
                'address_info_date': self.create_date,
                # 'cv_source_info_auth_type': 'dnic',
            }
            partner = Partner.with_context(can_update_contact_cv=True).create(data_partner)
            partner.suspend_security().update_dnic_values()
            is_dnic_info_complete = partner.cv_dnic_name_1 and partner.cv_dnic_lastname_1
            if (not partner.cv_first_name or not partner.cv_last_name_1) and is_dnic_info_complete:
                partner.write({
                    'cv_first_name': partner.cv_dnic_name_1,
                    'cv_second_name': partner.cv_dnic_name_2,
                    'cv_last_name_1': partner.cv_dnic_lastname_1,
                    'cv_last_name_2': partner.cv_dnic_lastname_2,
                })
        return partner

    def _create_cv(self, partner_id):
        CVDigital = self.env['onsc.cv.digital'].suspend_security()
        try:
            data = {
                'partner_id': partner_id.id,
                'personal_phone': self.personal_phone,
                'mobile_phone': self.mobile_phone,
                'email': self.email,
                'country_id': self.country_id.id,
                'marital_status_id': self.marital_status_id.id,
                'country_of_birth_id': self.country_of_birth_id.id,
                'uy_citizenship': self.uy_citizenship,
                'crendencial_serie': self.crendencial_serie,
                'credential_number': self.credential_number,
                'cv_address_state_id': self.cv_address_state_id.id,
                'cv_address_location_id': self.cv_address_location_id.id,
                'cv_address_street2_id': self.cv_address_street2_id.id,
                'cv_address_street3_id': self.cv_address_street3_id.id,
                'cv_address_zip': self.cv_address_zip,
                'cv_address_nro_door': self.cv_address_nro_door,
                'cv_address_is_cv_bis': self.cv_address_is_cv_bis,
                'cv_address_apto': self.cv_address_apto,
                'cv_address_place': self.cv_address_place,
                'cv_address_block': self.cv_address_block,
                'cv_address_sandlot': self.cv_address_sandlot,
                'cv_address_amplification': self.cv_address_amplification,
                'institutional_email': self.email,
                # 'legajo_gral_info_documentary_validation_state': 'validated',
            }
            return CVDigital.create(data)
        except Exception as e:
            raise ValidationError(_("No se pudo crear el CV: ") + tools.ustr(e))
