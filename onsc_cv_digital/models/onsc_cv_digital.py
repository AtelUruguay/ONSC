# -*- coding: utf-8 -*-

from lxml import etree
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

from .catalogs.res_partner import CV_SEX

html2construct = """<a     class="btn btn-outline-dark" target="_blank" title="Enlace a la ayuda"
                            href="%(url)s">
                            <i class="fa fa-question-circle-o" role="img" aria-label="Info"/>Ayuda</a>"""


class ONSCCVDigital(models.Model):
    _name = 'onsc.cv.digital'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Currículum digital'
    _rec_name = 'cv_full_name'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ONSCCVDigital, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                         submenu=submenu)
        if self.env.user.has_group('onsc_cv_digital.group_user_cv') and self.search_count(
                [('partner_id', '=', self.env.user.partner_id.id), ('active', 'in', [False, True])]):
            doc = etree.XML(res['arch'])
            if view_type in ['form', 'tree', 'kanban']:
                for node_form in doc.xpath("//%s" % (view_type)):
                    node_form.set('create', '0')
            res['arch'] = etree.tostring(doc)
        return res

    def _default_partner_id(self):
        return self.env['res.partner'].search([('user_ids', 'in', self.env.user.id)], limit=1)

    partner_id = fields.Many2one(
        "res.partner",
        string="Contacto",
        required=True, index=True,
        default=_default_partner_id)
    active = fields.Boolean(
        string="Activo", default=True)
    is_partner_cv = fields.Boolean(u'¿Es un contacto de CV?')
    is_cv_uruguay = fields.Boolean(
        string='¿Es documento uruguayo?',
        related='partner_id.is_cv_uruguay', store=True)
    cv_full_name = fields.Char('Nombre', related='partner_id.cv_full_name', store=True)

    cv_emissor_country_id = fields.Many2one(
        'res.country',
        string=u'País emisor del documento',
        related='partner_id.cv_emissor_country_id', store=True, tracking=True)
    cv_document_type_id = fields.Many2one(
        'onsc.cv.document.type',
        string=u'Tipo de documento',
        related='partner_id.cv_document_type_id', store=True, tracking=True)
    cv_nro_doc = fields.Char(
        string=u'Número de documento',
        related='partner_id.cv_nro_doc', store=True, tracking=True)
    image_1920 = fields.Image(
        string="Image",
        max_width=1920, max_height=1920,
        related='partner_id.image_1920', store=True, readonly=False, tracking=True)
    avatar_128 = fields.Image(
        string="Avatar 128",
        max_width=128, max_height=128,
        related='partner_id.avatar_128')
    cv_birthdate = fields.Date(
        string=u'Fecha de nacimiento',
        related='partner_id.cv_birthdate', store=True, readonly=False, tracking=True)
    cv_sex = fields.Selection(
        CV_SEX,
        string=u'Sexo',
        related='partner_id.cv_sex', store=True, readonly=False, tracking=True)
    cv_sex_updated_date = fields.Date(
        string=u'Fecha de información sexo',
        related='partner_id.cv_sex_updated_date', store=True, readonly=False, tracking=True)
    cv_expiration_date = fields.Date(
        string=u'Fecha de vencimiento documento de identidad',
        related='partner_id.cv_expiration_date', store=True, readonly=False, tracking=True)
    email = fields.Char(
        string="Email",
        related='partner_id.email', store=True)

    # INFORMACION GENERAL---<Page>
    # Genero
    cv_gender_id = fields.Many2one("onsc.cv.gender", string=u"Género", required=True, )
    is_cv_gender_option_other_enable = fields.Boolean(
        u'¿Permitir opción otra/o?',
        related='cv_gender_id.is_option_other_enable',
        store=True)
    cv_gender2 = fields.Char(string=u"Otro género")
    cv_gender_record = fields.Binary(string="Constancia de identidad de género")
    is_cv_gender_public = fields.Boolean(string="¿Permite que su género sea público?")
    is_cv_gender_record = fields.Boolean(u'Constancia', related='cv_gender_id.record')
    # Raza
    cv_race_ids = fields.Many2many("onsc.cv.race", string=u"Raza", required=True,
                                   domain="[('race_type','in',['race','both'])]")
    is_cv_race_option_other_enable = fields.Boolean(
        u'¿Permitir opción otra/o?',
        compute='_compute_cv_race_values', store=True)
    is_multiple_cv_race_selected = fields.Boolean(
        u'Múltiples razas seleccionadas',
        compute='_compute_cv_race_values', store=True)
    cv_race2 = fields.Char(string=u"Otra raza")
    cv_first_race_id = fields.Many2one("onsc.cv.race", string="¿Con que raza se reconoce principalmente?",
                                       domain="[('id','in',cv_race_ids)]")
    is_cv_race_public = fields.Boolean(string="¿Permite que su raza sea público?")
    # Información patronímica
    cv_full_name_updated_date = fields.Date(related='partner_id.cv_full_name_updated_date',
                                            string="Fecha de información")

    # DOMICILIO----<Page>
    country_id = fields.Many2one(related='partner_id.country_id')
    cv_address_state_id = fields.Many2one(related='partner_id.state_id')
    cv_address_location_id = fields.Many2one(related='partner_id.cv_location_id')
    cv_address_street = fields.Char(related='partner_id.street')
    cv_address_nro_door = fields.Char(related='partner_id.cv_nro_door')
    cv_address_apto = fields.Char(related='partner_id.cv_apto')
    cv_address_street2 = fields.Char(related='partner_id.street2')
    cv_address_street3 = fields.Char(related='partner_id.cv_street3')
    cv_address_zip = fields.Char(related='partner_id.zip')
    cv_address_is_cv_bis = fields.Boolean(related='partner_id.is_cv_bis')
    cv_address_amplification = fields.Text(related='partner_id.cv_amplification')
    cv_address_state = fields.Selection(related='cv_address_location_id.state')
    cv_address_reject_reason = fields.Char(related='cv_address_location_id.reject_reason')
    # Help online
    cv_help_general_info = fields.Html(
        compute=lambda s: s._get_help('cv_help_general_info'), store=False, readonly=True)
    cv_help_address = fields.Html(
        compute=lambda s: s._get_help('cv_help_address'), store=False, readonly=True)

    country_of_birth_id = fields.Many2one("res.country", string="País de nacimiento", required=True)
    uruguayan_citizenship = fields.Selection(string="Ciudadanía Uruguaya",
                                             selection=[('legal', 'Legal'), ('natural', 'Natural'),
                                                        ('extranjero', 'Extranjero')], required=True)
    marital_status_id = fields.Many2one("onsc.cv.status.civil", string="Estado Civil", required=True)
    credential_series = fields.Char(string="Serie de la credencial", size=3)
    credential_number = fields.Integer(string="Numero de la credencial")
    cjppu_affiliate_number = fields.Integer(string="Numero de afiliado a la CJPPU")
    professional_resume = fields.Text(string="Resumen profesional")
    user_linkedIn = fields.Char(string="Usuario en LinkedIn")
    is_afro_descendants = fields.Boolean(string="Afrodescendientes (Art. 4 Ley N°19.122)")
    document_afro_descendants = fields.Binary(
        string='Documento digitalizado "Declaración de Afrodescendencia" / Formulario web de Declaración jurada de Afrodescendencia (Art. 4 Ley N°19.122) ')
    is_driver_license = fields.Boolean(string="Tiene licencia de conducir")
    cv_digital_drivers_license = fields.One2many("onsc.cv.digital.driver.license",
                                                 inverse_name="cv_digital_id", string="Licencias de Conducir")

    personal_phone = fields.Char(string="Teléfono particular", related='partner_id.phone', readonly=False)
    mobile_phone = fields.Char(string="Teléfono celular", related='partner_id.mobile', readonly=False)
    email = fields.Char(string="Email", related='partner_id.email')

    is_occupational_health_card = fields.Boolean(string="Carné de Salud Laboral")
    occupational_health_card_date = fields.Date(string="Fecha de vencimiento del Carné de Salud Laboral")
    digital_document_occupational_health_card = fields.Binary(
        string="Documento digitalizado del Carné de Salud Laboral")

    digital_document_document_identity = fields.Binary(string="Documento digitalizado del Documento de Identidad")
    digital_document_document_identity_attachment_id = fields.Many2one("ir.attachment",
                                                                       string="Documento digitalizado del Documento de Identidad adjunto",
                                                                       compute="_compute_digital_documents", store=True)

    document_identity_validation_status = fields.Selection(string="Estado validación documental – doc. Identidad",
                                                           related='digital_document_document_identity_attachment_id.validation_status')
    reject_reason_document_identity = fields.Char(string="Motivo rechazo validación documental – doc. Identidad",
                                                  related='digital_document_document_identity_attachment_id.reject_reason')

    digital_document_civical_credential = fields.Binary(string="Documento digitalizado Credencial cívica",
                                                        required=False, )
    digital_document_civical_credential_attachment_id = fields.Many2one("ir.attachment",
                                                                        string="Documento digitalizado Credencial cívica adjunto",
                                                                        compute="_compute_digital_documents",
                                                                        store=True)
    digital_document_civical_credential_status = fields.Selection(
        string="Estado validación documental – Credencial cívica",
        related='digital_document_civical_credential_attachment_id.validation_status')
    reject_reason_civical_credential = fields.Char(string="Motivo rechazo validación documental – Credencial cívica",
                                                   related='digital_document_civical_credential_attachment_id.reject_reason')

    sports_medical_aptitude_certificate_status = fields.Selection(string="Certificado de aptitud médico-deportiva",
                                                                  selection=[('si', 'Si'), ('no', 'No'), ])
    sports_medical_aptitude_certificate_date = fields.Date(
        string="Fecha de vencimiento del Certificado de aptitud médico-deportiva")
    digital_document_sports_medical_aptitude_certificate = fields.Binary(
        string="Documento digitalizado del Certificado de aptitud médico-deportiva")

    is_victim_violent = fields.Boolean(string="Persona víctima de delitos violentos (Art. 105 Ley Nº 19.889)", )
    digital_document_relationship_victim_violent = fields.Binary(
        string="Documento digitalizado: Comprobante de parentesco con persona víctima de delito violento")
    is_public_information_victim_violent = fields.Boolean(
        string="¿Permite que su información de persona víctima de delitos violentos sea público?", )

    @api.constrains('cv_sex_updated_date', 'cv_birthdate')
    def _check_valid_dates(self):
        today = fields.Date.from_string(fields.Date.today())
        for record in self:
            if fields.Date.from_string(record.cv_sex_updated_date) > today:
                raise ValidationError(_("La Fecha de información sexo no puede ser posterior a la fecha actual"))
            if fields.Date.from_string(record.cv_birthdate) > today:
                raise ValidationError(_("La Fecha de nacimiento no puede ser posterior a la fecha actual"))

    def _get_help(self, help_field=''):
        _url = eval('self.env.user.company_id.%s' % (help_field))
        _html2construct = html2construct % {'url': _url}
        for rec in self:
            setattr(rec, help_field, _html2construct)

    @api.depends('cv_race_ids')
    def _compute_cv_race_values(self):
        for record in self:
            record.is_cv_race_option_other_enable = len(
                record.cv_race_ids.filtered(lambda x: x.is_option_other_enable)) > 0
            record.is_multiple_cv_race_selected = len(record.cv_race_ids) > 1

    def _action_open_user_cv(self):
        vals = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': self._name,
            'name': 'Curriculum vitae',
            'context': self.env.context
        }
        if self.env.user.has_group('onsc_cv_digital.group_user_cv'):
            my_cv = self.search([
                ('partner_id', '=', self.env.user.partner_id.id), ('active', 'in', [False, True])], limit=1)
            if my_cv:
                vals.update({'res_id': my_cv.id})
        return vals

    def button_edit_address(self):
        self.ensure_one()
        title = self.country_id and _('Editar domicilio') or _('Agregar domicilio')
        ctx = self._context.copy()
        wizard = self.env['onsc.cv.address.wizard'].create({'partner_id': self.partner_id.id})
        return {
            'name': title,
            'view_mode': 'form',
            'res_model': 'onsc.cv.address.wizard',
            'target': 'new',
            'view_id': False,
            'res_id': wizard.id,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    def button_active_cv(self):
        self.write({'active': True})

    @api.constrains('personal_phone', 'mobile_phone')
    def _check_valid_phone(self):
        for record in self:
            if not record.personal_phone and not record.mobile_phone:
                raise ValidationError(_("Necesitas al menos introducir la información de un teléfono"))

    @api.depends('digital_document_civical_credential_attachment_id',
                 'digital_document_document_identity_attachment_id')
    def _compute_digital_documents(self):
        attachment_objec = self.env['ir.attachment']
        for rec in self:
            rec.digital_document_civical_credential_attachment_id = attachment_objec.search(
                [('res_model', '=', 'onsc.cv.digital'), ('res_id', '=', rec.id),
                 ('res_field', '=', 'digital_document_civical_credential')], limit=1)
            rec.digital_document_document_identity_attachment_id = attachment_objec.search(
                [('res_model', '=', 'onsc.cv.digital'), ('res_id', '=', rec.id),
                 ('res_field', '=', 'digital_document_document_identity')], limit=1)
