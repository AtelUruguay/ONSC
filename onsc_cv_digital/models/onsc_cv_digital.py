# -*- coding: utf-8 -*-

import logging

from lxml import etree
from odoo import fields, models, api, _
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as cv_warning
from odoo.exceptions import ValidationError
from zeep import Client
from zeep.exceptions import Fault

from .abstracts.onsc_cv_abstract_documentary_validation import DOCUMENTARY_VALIDATION_STATES

_logger = logging.getLogger(__name__)

HTML_HELP = """<a     class="btn btn-outline-dark" target="_blank" title="Enlace a la ayuda"
                            href="%s">
                            <i class="fa fa-question-circle-o" role="img" aria-label="Info"/>Ayuda</a>"""
SELECTION_RADIO = [('1', 'Si, no puede hacerlo'), ('2', 'Si, mucha dificultad'),
                   ('3', 'Si, alguna dificultad '), ('4', 'No tiene dificultad')]
SITUATION = u'¿Está en situación de discapacidad y/o requiere algún apoyo para cumplir con sus actividades laborales?'
DISABILITE = u'¿Está inscripto en el registro de personas con discapacidad del Ministerio de Desarrollo Social?'


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


class ONSCCVDigital(models.Model):
    _name = 'onsc.cv.digital'
    _description = 'Currículum digital'
    _rec_name = 'cv_full_name'
    _inherit = 'onsc.cv.abstract.phone.validated'

    @property
    def prefix_by_phones(self):
        res = super().prefix_by_phones
        return res + [('prefix_phone_id', 'personal_phone'), ('prefix_mobile_phone_id', 'mobile_phone')]

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ONSCCVDigital, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                         submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type in ['form', 'tree', 'kanban']:
            if self.env.user.has_group('onsc_cv_digital.group_user_cv') and self.search_count(
                    [('partner_id', '=', self.env.user.partner_id.id), ('active', 'in', [False, True])]):
                for node_form in doc.xpath("//%s" % (view_type)):
                    node_form.set('create', '0')
            if self.env.user.has_group('onsc_cv_digital.group_manager_cv'):
                for node_form in doc.xpath("//%s" % (view_type)):
                    node_form.set('edit', '0')
        res['arch'] = etree.tostring(doc)
        return res

    def _default_partner_id(self):
        return self.env['res.partner'].search([('user_ids', 'in', self.env.user.id)], limit=1)

    partner_id = fields.Many2one(
        "res.partner",
        string="Contacto",
        required=True, index=True,
        default=_default_partner_id)
    type = fields.Selection(string=u"Tipo", selection=[('cv', 'CV'), ('call', 'Llamado')],
                            required=True,
                            index=True,
                            default='cv')
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
        related='partner_id.cv_emissor_country_id', store=True)
    cv_document_type_id = fields.Many2one(
        'onsc.cv.document.type',
        string=u'Tipo de documento',
        related='partner_id.cv_document_type_id', store=True)
    cv_nro_doc = fields.Char(
        string=u'Número de documento',
        related='partner_id.cv_nro_doc', store=True)
    image_1920 = fields.Image(
        string="Image",
        max_width=1920, max_height=1920,
        related='partner_id.image_1920', store=True, readonly=False)
    avatar_128 = fields.Image(
        string="Avatar 128",
        max_width=128, max_height=128,
        related='partner_id.avatar_128')
    cv_birthdate = fields.Date(
        string=u'Fecha de nacimiento',
        related='partner_id.cv_birthdate', store=True, readonly=False)
    cv_sex = fields.Selection(
        string=u'Sexo',
        related='partner_id.cv_sex', store=True, readonly=False)
    cv_sex_updated_date = fields.Date(
        string=u'Fecha de información sexo',
        related='partner_id.cv_sex_updated_date', store=True, readonly=False)
    cv_expiration_date = fields.Date(
        string=u'Fecha de vencimiento documento de identidad',
        related='partner_id.cv_expiration_date', store=True, readonly=False)
    email = fields.Char(
        string="Email",
        related='partner_id.email', store=True)
    last_modification_date = fields.Date(string=u'Fecha última modificación', store=True,
                                         compute='_compute_last_modification_date', readonly=True)

    # INFORMACION GENERAL---<Page>
    # Genero
    cv_gender_id = fields.Many2one("onsc.cv.gender", string=u"Género", required=True, )
    is_cv_gender_option_other_enable = fields.Boolean(
        u'¿Permitir opción otra/o?',
        related='cv_gender_id.is_option_other_enable',
        store=True)
    cv_gender2 = fields.Char(string=u"Otro género")
    cv_gender_record_file = fields.Binary(string="Constancia de identidad de género")
    cv_gender_record_filename = fields.Char('Nombre del documento digital')
    is_cv_gender_public = fields.Boolean(
        string="¿Desea que esta información se incluya en la versión impresa de su CV?")
    is_cv_gender_record = fields.Boolean(u'Constancia', related='cv_gender_id.record')
    # Raza
    cv_race_ids = fields.Many2many("onsc.cv.race", string=u"Identidad étnico-racial", required=True,
                                   domain="[('race_type','in',['race','both'])]")
    is_cv_race_option_other_enable = fields.Boolean(
        u'¿Permitir opción otra/o?',
        compute='_compute_cv_race_values', store=True)
    is_multiple_cv_race_selected = fields.Boolean(
        u'Múltiples razas seleccionadas',
        compute='_compute_cv_race_values', store=True)
    cv_race2 = fields.Char(string=u"Otra identidad étnico-racial")
    cv_first_race_id = fields.Many2one("onsc.cv.race", string=u"¿Con cuál se reconoce principalmente?",
                                       domain="[('id','in',cv_race_ids)]")
    is_cv_race_public = fields.Boolean(string="¿Permite que su identidad étnico-racial se visualice en su CV?")
    # Información patronímica
    cv_full_name_updated_date = fields.Date(related='partner_id.cv_full_name_updated_date',
                                            string="Fecha de información")

    # DOMICILIO----<Page>
    country_id = fields.Many2one(related='partner_id.country_id', readonly=False)
    country_code = fields.Char("Código", related="country_id.code", readonly=True)
    cv_address_state_id = fields.Many2one(related='partner_id.state_id', readonly=False)
    cv_address_location_id = fields.Many2one(related='partner_id.cv_location_id', readonly=False, store=True)
    cv_address_street_id = fields.Many2one('onsc.cv.street', string="Calle")
    cv_address_street2_id = fields.Many2one('onsc.cv.street', string="Entre calle")
    cv_address_street3_id = fields.Many2one('onsc.cv.street', string=u'Y calle')
    cv_address_nro_door = fields.Char(related='partner_id.cv_nro_door', readonly=False)
    cv_address_apto = fields.Char(related='partner_id.cv_apto', readonly=False)
    cv_address_street = fields.Char(related='partner_id.street', readonly=False)
    cv_address_zip = fields.Char(related='partner_id.zip', readonly=False)
    cv_address_is_cv_bis = fields.Boolean(related='partner_id.is_cv_bis', readonly=False)
    cv_address_amplification = fields.Text(related='partner_id.cv_amplification', readonly=False)
    cv_address_state = fields.Selection(related='cv_address_location_id.state', store=True)
    cv_address_reject_reason = fields.Text(related='cv_address_location_id.reject_reason')
    cv_address_place = fields.Text(related='partner_id.cv_address_place', string="Paraje", size=200, readonly=False)
    cv_address_block = fields.Char(related='partner_id.cv_address_block', string="Manzana", size=5, readonly=False)
    cv_address_sandlot = fields.Char(related='partner_id.cv_address_sandlot', string="Solar", size=5, readonly=False)
    country_of_birth_id = fields.Many2one("res.country", string="País de nacimiento", required=True)
    uy_citizenship = fields.Selection(string="Ciudadanía uruguaya",
                                      selection=[('legal', 'Legal'), ('natural', 'Natural'),
                                                 ('extranjero', 'Extranjero')], required=True)
    marital_status_id = fields.Many2one("onsc.cv.status.civil", string="Estado civil", required=True)
    crendencial_serie = fields.Char(string="Serie de la credencial", size=3)
    credential_number = fields.Char(string="Numero de la credencial", size=6)
    cjppu_affiliate_number = fields.Integer(string="Numero de afiliado a la CJPPU")
    professional_resume = fields.Text(string="Resumen profesional")
    user_linkedIn = fields.Char(string="Usuario en LinkedIn")
    is_afro_descendants = fields.Boolean(string="Afrodescendientes (Art. 4 Ley N°19.122)")
    afro_descendants_file = fields.Binary(
        string='Documento digitalizado "Declaración de afrodescendencia (Art. 4 Ley N°19.122)"')
    afro_descendants_filename = fields.Char('Nombre del documento digital')
    is_driver_license = fields.Boolean(string="¿Tiene licencia de conducir?")
    drivers_license_ids = fields.One2many("onsc.cv.driver.license",
                                          inverse_name="cv_digital_id", string="Licencias de conducir", copy=True)

    prefix_phone_id = fields.Many2one(related='partner_id.prefix_phone_id', readonly=False)
    personal_phone = fields.Char(string="Teléfono particular", related='partner_id.phone', readonly=False)
    prefix_mobile_phone_id = fields.Many2one(related='partner_id.prefix_mobile_phone_id', readonly=False)
    mobile_phone = fields.Char(string="Teléfono celular", related='partner_id.mobile', readonly=False)
    email = fields.Char(string="Email", related='partner_id.email')

    is_occupational_health_card = fields.Boolean(string="¿Tiene carné de salud laboral?")
    occupational_health_card_date = fields.Date(string="Fecha de vencimiento del carné de salud laboral")
    occupational_health_card_file = fields.Binary(
        string="Documento digitalizado del carné de salud laboral")
    occupational_health_card_filename = fields.Char('Nombre del documento digital')

    document_identity_file = fields.Binary(string="Documento digitalizado del documento de identidad")
    document_identity_filename = fields.Char('Nombre del documento digital')

    civical_credential_file = fields.Binary(string="Documento digitalizado credencial cívica")
    civical_credential_filename = fields.Char('Nombre del documento digital')
    is_medical_aptitude_certificate_status = fields.Boolean(
        string="¿Tiene certificado de aptitud médico-deportiva?")
    medical_aptitude_certificate_date = fields.Date(
        string="Fecha de vencimiento del certificado de aptitud médico-deportiva")
    medical_aptitude_certificate_file = fields.Binary(
        string="Documento digitalizado del certificado de aptitud médico-deportiva")
    medical_aptitude_certificate_filename = fields.Char('Nombre del documento digital')

    is_victim_violent = fields.Boolean(string="Persona víctima de delitos violentos (Art. 105 Ley Nº 19.889)", )
    relationship_victim_violent_file = fields.Binary(
        string="Documento digitalizado: Comprobante de parentesco con persona víctima de delito violento")
    relationship_victim_violent_filename = fields.Char('Nombre del documento digital')
    is_public_information_victim_violent = fields.Boolean(
        string="¿Desea que esta información se incluya en la versión impresa de su CV?", )

    # Formación----<Page>
    basic_formation_ids = fields.One2many('onsc.cv.basic.formation', 'cv_digital_id', string=u'Formación básica',
                                          copy=True)
    advanced_formation_ids = fields.One2many('onsc.cv.advanced.formation', 'cv_digital_id',
                                             string=u'Formación avanzada', copy=True)
    # Cursos y certificado----<Page>
    course_certificate_ids = fields.One2many('onsc.cv.course.certificate', inverse_name='cv_digital_id',
                                             string="Cursos y certificados", copy=True)
    course_ids = fields.One2many('onsc.cv.course.certificate', inverse_name='cv_digital_id',
                                 string="Cursos", domain=[('record_type', '=', 'course')], copy=False)
    certificate_ids = fields.One2many('onsc.cv.course.certificate', inverse_name='cv_digital_id',
                                      string="Certificados", domain=[('record_type', '=', 'certificate')], copy=False)
    # Experiencia Laboral ----<Page>
    work_experience_ids = fields.One2many("onsc.cv.work.experience", inverse_name="cv_digital_id",
                                          string="Experiencia laboral", copy=True)
    # Docencia ----<Page>
    work_teaching_ids = fields.One2many('onsc.cv.work.teaching', inverse_name='cv_digital_id', string='Docencia',
                                        copy=True)
    # Investigación ----<Page>
    work_investigation_ids = fields.One2many('onsc.cv.work.investigation', inverse_name='cv_digital_id',
                                             string='Investigación', copy=True)
    # Voluntariado ----<Page>
    volunteering_ids = fields.One2many("onsc.cv.volunteering", inverse_name="cv_digital_id", string="Voluntariado",
                                       copy=True)
    # Idioma ----<Page>
    language_level_ids = fields.One2many('onsc.cv.language.level', inverse_name='cv_digital_id', string='Idiomas',
                                         copy=True)
    # Publicaciones, Producciones y Evaluaciones ----<Page>
    publication_production_evaluation_ids = fields.One2many("onsc.cv.publication.production.evaluation",
                                                            inverse_name="cv_digital_id",
                                                            string="Publicaciones, producciones y evaluaciones",
                                                            copy=True)
    # Tutorías, Orientaciones, Supervisiones ----<Page>
    tutoring_orientation_supervision_ids = fields.One2many('onsc.cv.tutoring.orientation.supervision',
                                                           inverse_name="cv_digital_id",
                                                           string="Tutorías, Orientaciones, Supervisiones", copy=True)
    # Discapacidad ----<Page>
    allow_content_public = fields.Selection(selection=[('si', u'Si'), ('no', u'No')], default='no', required=True,
                                            string=u'¿Permite que el contenido de esta sección se visualice en su CV?')
    situation_disability = fields.Selection(selection=[('si', u'Si'), ('no', u'No')], string=SITUATION)
    people_disabilitie = fields.Selection(selection=[('si', u'Si'), ('no', u'No')], string=DISABILITE)
    document_certificate_file = fields.Binary(string=u'Documento digitalizado constancia de inscripción en el RNPcD')
    document_certificate_filename = fields.Char('Nombre del documento Digitalizado')
    certificate_date = fields.Date(string=u'Fecha de certificado')
    to_date = fields.Date(string=u'Fecha hasta')
    see = fields.Selection(selection=SELECTION_RADIO, string=u'Ver, aún si usa anteojos o lentes')
    hear = fields.Selection(selection=SELECTION_RADIO, string=u'Oír, aún si usa audífono')
    walk = fields.Selection(selection=SELECTION_RADIO, string=u'Caminar o subir escalones')
    speak = fields.Selection(selection=SELECTION_RADIO, string=u'Hablar o comunicarse aún usando lengua de señas')
    realize = fields.Selection(selection=SELECTION_RADIO,
                               string=u'Realizar tareas de cuidado personal como comer, bañarse o vestirse solo')
    lear = fields.Selection(selection=SELECTION_RADIO, string=u'Entender y/o aprender')
    interaction = fields.Selection(selection=SELECTION_RADIO, string=u'Interactuar y/o relacionarse con otras personas')
    type_support_ids = fields.Many2many('onsc.cv.type.support', 'type_support_id', string=u'Tipos de apoyo', copy=True)
    type_support_ids_domain = fields.Many2many('onsc.cv.type.support', 'type_support_domain_id',
                                               compute='_compute_cv_type_support_domain', copy=True)
    need_other_support = fields.Text(string=u"¿Necesita otro apoyo?")
    is_need_other_support = fields.Boolean(compute='_compute_cv_type_support_domain')

    # Participación en Eventos ----<Page>
    participation_event_ids = fields.One2many("onsc.cv.participation.event",
                                              inverse_name="cv_digital_id",
                                              string="Participación en eventos", copy=True)
    # Otra información relevante ----<Page>
    other_relevant_information_ids = fields.One2many("onsc.cv.other.relevant.information",
                                                     inverse_name="cv_digital_id",
                                                     string="Otra información relevante", copy=True)
    # Referencias ------<Page>
    reference_ids = fields.One2many('onsc.cv.reference', inverse_name='cv_digital_id', string='Referencias', copy=True)

    is_cv_uruguay_ci = fields.Boolean('¿Es documento uruguayo?', compute='_compute_is_cv_uruguay_ci')

    # Help online
    cv_help_general_info = fields.Html(
        compute=lambda s: s._get_help('cv_help_general_info'),
        default=lambda s: s._get_help('cv_help_general_info', True))
    cv_help_address = fields.Html(
        compute=lambda s: s._get_help('cv_help_address'),
        default=lambda s: s._get_help('cv_help_address', True)
    )
    cv_help_work_experience = fields.Html(
        compute=lambda s: s._get_help('cv_help_work_experience'),
        default=lambda s: s._get_help('cv_help_work_experience', True)
    )
    cv_help_work_teaching = fields.Html(
        compute=lambda s: s._get_help('cv_help_work_teaching'),
        default=lambda s: s._get_help('cv_help_work_teaching', True)
    )
    cv_help_work_investigation = fields.Html(
        compute=lambda s: s._get_help('cv_help_work_investigation'),
        default=lambda s: s._get_help('cv_help_work_investigation', True)
    )
    cv_help_formation = fields.Html(
        compute=lambda s: s._get_help('cv_help_formation'),
        default=lambda s: s._get_help('cv_help_formation', True)
    )
    cv_help_course_certificate = fields.Html(
        compute=lambda s: s._get_help('cv_help_course_certificate'),
        default=lambda s: s._get_help('cv_help_course_certificate', True)
    )
    cv_help_volunteering = fields.Html(
        compute=lambda s: s._get_help('cv_help_volunteering'),
        default=lambda s: s._get_help('cv_help_volunteering', True)
    )
    cv_help_language_level = fields.Html(
        compute=lambda s: s._get_help('cv_help_language_level'),
        default=lambda s: s._get_help('cv_help_language_level', True)
    )
    cv_help_publications_productions_evaluations = fields.Html(
        compute=lambda s: s._get_help('cv_help_publications_productions_evaluations'),
        default=lambda s: s._get_help('cv_help_publications_productions_evaluations', True)
    )
    cv_help_tutoring_orientation_supervision = fields.Html(
        compute=lambda s: s._get_help('cv_help_tutoring_orientation_supervision'),
        default=lambda s: s._get_help('cv_help_tutoring_orientation_supervision', True)
    )
    cv_help_disability = fields.Html(
        compute=lambda s: s._get_help('cv_help_disability'),
        default=lambda s: s._get_help('cv_help_disability', True)
    )
    cv_help_participation_event = fields.Html(
        compute=lambda s: s._get_help('cv_help_participation_event'),
        default=lambda s: s._get_help('cv_help_participation_event', True)
    )
    cv_help_other_relevant_information = fields.Html(
        compute=lambda s: s._get_help('cv_help_other_relevant_information'),
        default=lambda s: s._get_help('cv_help_other_relevant_information', True)
    )
    cv_help_reference = fields.Html(
        compute=lambda s: s._get_help('cv_help_reference'),
        default=lambda s: s._get_help('cv_help_reference', True)
    )

    # VALIDACION DOCUMENTAL
    # DISCAPACIDAD
    disabilitie_documentary_validation_state = fields.Selection(
        string="Estado de validación documental",
        selection=DOCUMENTARY_VALIDATION_STATES,
        default='to_validate')
    disabilitie_write_date = fields.Datetime('Fecha de última modificación',
                                             index=True,
                                             default=lambda *a: fields.Datetime.now())
    disabilitie_documentary_reject_reason = fields.Text(string=u'Motivo de rechazo validación documental',
                                                        tracking=True)
    disabilitie_documentary_validation_date = fields.Date(u'Fecha validación documental', tracking=True)
    disabilitie_documentary_user_id = fields.Many2one(comodel_name="res.users", string="Usuario validación documental",
                                                      tracking=True)

    # NRO DOC
    nro_doc_documentary_validation_state = fields.Selection(
        string="Estado de validación documental",
        selection=DOCUMENTARY_VALIDATION_STATES,
        default='to_validate')
    nro_doc_write_date = fields.Datetime('Fecha de última modificación',
                                         index=True,
                                         default=lambda *a: fields.Datetime.now())
    nro_doc_documentary_reject_reason = fields.Text(string=u'Motivo de rechazo validación documental', tracking=True)
    nro_doc_documentary_validation_date = fields.Date(u'Fecha validación documental', tracking=True)
    nro_doc_documentary_user_id = fields.Many2one(comodel_name="res.users", string="Usuario validación documental",
                                                  tracking=True)
    # CREDENCIAL CIVICA
    civical_credential_documentary_validation_state = fields.Selection(
        string="Estado de validación documental",
        selection=DOCUMENTARY_VALIDATION_STATES,
        default='to_validate')
    civical_credential_write_date = fields.Datetime('Fecha de última modificación',
                                                    index=True,
                                                    default=lambda *a: fields.Datetime.now())
    civical_credential_documentary_reject_reason = fields.Text(string=u'Motivo de rechazo validación documental',
                                                               tracking=True)
    civical_credential_documentary_validation_date = fields.Date(u'Fecha validación documental', tracking=True)
    civical_credential_documentary_user_id = fields.Many2one(comodel_name="res.users",
                                                             string="Usuario validación documental",
                                                             tracking=True)

    def _get_help(self, help_field='', is_default=False):
        _url = eval('self.env.user.company_id.%s' % help_field)
        _html2construct = HTML_HELP % (_url or '/')
        if is_default:
            return eval("_html2construct")
        for rec in self:
            setattr(rec, help_field, _html2construct)

    @api.depends('cv_race_ids')
    def _compute_cv_race_values(self):
        for record in self:
            record.is_cv_race_option_other_enable = len(
                record.cv_race_ids.filtered(lambda x: x.is_option_other_enable)) > 0
            record.is_multiple_cv_race_selected = len(record.cv_race_ids) > 1

    @api.depends('see', 'hear', 'walk', 'speak', 'realize', 'lear', 'interaction')
    def _compute_cv_type_support_domain(self):
        type_support_ids = []
        type_supports = self.env['onsc.cv.type.support'].search([])
        type_support_see = type_supports.filtered(lambda x: x.see)
        type_support_hear = type_supports.filtered(lambda x: x.hear)
        type_support_walk = type_supports.filtered(lambda x: x.walk)
        type_support_speak = type_supports.filtered(lambda x: x.talk)
        type_support_realize = type_supports.filtered(lambda x: x.slide)
        type_support_lear = type_supports.filtered(lambda x: x.understand)
        type_support_interaction = type_supports.filtered(lambda x: x.interaction)
        for record in self:
            if record.see and record.see != '4' and type_support_see:
                type_support_ids.extend(type_support_see.ids)
            if record.hear and record.hear != '4' and type_support_hear:
                type_support_ids.extend(type_support_hear.ids)
            if record.walk and record.walk != '4' and type_support_walk:
                type_support_ids.extend(type_support_walk.ids)
            if record.speak and record.speak != '4' and type_support_speak:
                type_support_ids.extend(type_support_speak.ids)
            if record.realize and record.realize != '4' and type_support_realize:
                type_support_ids.extend(type_support_realize.ids)
            if record.lear and record.lear != '4' and type_support_lear:
                type_support_ids.extend(type_support_lear.ids)
            if record.interaction and record.interaction != '4' and type_support_interaction:
                type_support_ids.extend(type_support_interaction.ids)
            if type_support_ids:
                record.is_need_other_support = True
            else:
                record.is_need_other_support = False
            record.type_support_ids_domain = type_support_ids

    @api.depends(lambda model: ('create_date', 'write_date') if model._log_access else ())
    def _compute_last_modification_date(self):
        if self._log_access:
            for record in self:
                record.last_modification_date = record.write_date or record.create_date or fields.Date.today()
        else:
            self.last_modification_date = fields.Date.today()

    @api.depends('cv_emissor_country_id', 'cv_document_type_id')
    def _compute_is_cv_uruguay_ci(self):
        for record in self:
            record.is_cv_uruguay_ci = record.cv_emissor_country_id.code == 'UY' and record.cv_document_type_id.code == 'ci'

    @api.constrains('cv_birthdate')
    def _check_valid_dates(self):
        today = fields.Date.from_string(fields.Date.today())
        for record in self:
            if record.cv_birthdate and fields.Date.from_string(record.cv_birthdate) > today:
                raise ValidationError(_("La Fecha de nacimiento no puede ser posterior a la fecha actual"))

    @api.constrains('crendencial_serie')
    def _check_crendencial_serie(self):
        for record in self:
            if len(record.crendencial_serie) != 3:
                raise ValidationError(_("La Serie de la credencial debe ser de 3 letras"))

    @api.constrains('personal_phone', 'mobile_phone')
    def _check_valid_phone(self):
        for record in self:
            if not record.personal_phone and not record.mobile_phone:
                raise ValidationError(_("Necesitas al menos introducir la información de un teléfono"))

    @api.onchange('cv_sex_updated_date')
    def onchange_cv_sex_updated_date(self):
        result = self.check_evaluation('cv_sex_updated_date')
        if result:
            self.cv_sex_updated_date = False
            return result

    @api.onchange('cv_birthdate')
    def onchange_cv_birthdate(self):
        result = self.check_evaluation('cv_birthdate')
        if result:
            self.cv_birthdate = False
            return result

    @api.onchange('country_id')
    def onchange_country_id(self):
        if self.cv_address_state_id.country_id.id != self.country_id.id:
            self.cv_address_state_id = False

    @api.onchange('cv_address_state_id')
    def onchange_cv_address_state_id(self):
        if self.cv_address_state_id:
            self.country_id = self.cv_address_state_id.country_id.id
        self.cv_address_location_id = False

    @api.onchange('certificate_date')
    def onchange_certificate_date(self):
        if self.certificate_date and self.to_date and self.to_date <= self.certificate_date:
            self.certificate_date = False
            return cv_warning(_("La fecha de certificado no puede ser mayor que la fecha hasta"))

    @api.onchange('to_date')
    def onchange_to_date(self):
        if self.to_date and self.certificate_date and self.to_date <= self.certificate_date:
            self.to_date = False
            return cv_warning(_("La fecha hasta no puede ser menor que la fecha de certificado"))

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
            return cv_warning(_("Solar no puden contener letras"))

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

    @api.onchange('is_occupational_health_card')
    def onchange_is_occupational_health_card(self):
        if self.is_occupational_health_card is False:
            self.occupational_health_card_date = False
            self.occupational_health_card_file = False
            self.occupational_health_card_file = False
            self.occupational_health_card_filename = False

    @api.onchange('is_medical_aptitude_certificate_status')
    def onchange_is_medical_aptitude_certificate_status(self):
        if self.is_medical_aptitude_certificate_status is False:
            self.medical_aptitude_certificate_date = False
            self.medical_aptitude_certificate_file = False
            self.medical_aptitude_certificate_filename = False

    @api.onchange('is_victim_violent')
    def onchange_is_victim_violent(self):
        if self.is_victim_violent is False:
            self.relationship_victim_violent_file = False
            self.relationship_victim_violent_filename = False

    @api.onchange('is_afro_descendants')
    def onchange_is_afro_descendants(self):
        if self.is_afro_descendants is False:
            self.afro_descendants_file = False
            self.afro_descendants_filename = False

    @api.onchange('situation_disability')
    def onchange_situation_disability(self):
        if self.situation_disability != 'si':
            self.see = False
            self.hear = False
            self.walk = False
            self.speak = False
            self.realize = False
            self.lear = False
            self.interaction = False
            self.type_support_ids = [(5,)]

    @api.onchange('people_disabilitie')
    def onchange_people_disabilitie(self):
        if self.people_disabilitie != 'si':
            self.document_certificate_file = False
            self.document_certificate_filename = False
            self.certificate_date = False
            self.to_date = False

    def button_unlink(self):
        self.unlink()
        return self._action_open_user_cv()

    def unlink(self):
        for record in self:
            if record._is_rve_link():
                raise ValidationError(_("No es posible eliminar su CV porque "
                                        "tiene o tuvo algún vínculo laboral con el Estado"))
        return super(ONSCCVDigital, self).unlink()

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

    def toggle_active(self):
        if len(self) and self[0].active is True:
            self._check_todisable()
        result = super().toggle_active()
        if len(self) == 1:
            return self.with_context(my_cv=self)._action_open_user_cv()
        return result

    def button_copy_cv(self):
        self.ensure_one()
        action = self.env.ref('onsc_cv_digital.onsc_cv_digital_call_mypostulations_action').sudo().read()[0]
        action['domain'] = "[('type','=','call'),('cv_digital_origin_id','in',%s)]" % self.ids
        return action

    def _action_open_user_cv(self):
        vals = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': self._name,
            'name': 'Curriculum vitae',
            'context': self.env.context
        }
        if self.env.user.has_group('onsc_cv_digital.group_user_cv'):
            my_cv = self._context.get('my_cv', False) or self.search(
                [('partner_id', '=', self.env.user.partner_id.id), ('active', 'in', [False, True]),
                 ('type', '=', 'cv')], limit=1)
            if my_cv and my_cv.active is False:
                vals.update({'views': [(self.get_readonly_formview_id(), 'form')]})
            vals.update({'res_id': my_cv.id})
        return vals

    def get_readonly_formview_id(self):
        """
        Crea una vista form con campos readonly la primera vez y luego es llamada si el CV está inactivo
        permiso de escribir"""
        # Hardcode the form view
        self = self.sudo()
        form_id = self.env['ir.ui.view'].search([('name', '=', '%s.form.readonly' % self._name)], limit=1)
        if not form_id:
            form_parent_id = self.env['ir.ui.view'].search([
                ('model', '=', self._name),
                ('type', '=', 'form')],
                order='id ASC', limit=1)
            if form_parent_id:
                arch = form_parent_id.arch
                doc = etree.XML(arch)
                for node_form in doc.xpath("//form"):
                    node_form.set('edit', '0')
                form_id = self.env['ir.ui.view'].create(
                    {'name': '%s.form.readonly' % self._name,
                     'type': 'form',
                     "model": self._name,
                     "priority": 100,
                     'arch': etree.tostring(doc, encoding='unicode')
                     })

        return form_id.id

    def check_evaluation(self, changed_field):
        """
        Utilizada para mostrar mensajes de advertencia en onchange de evaluacion
        :return:
        """
        result = {
            'warning': {
                'title': _("Atención"),
                'type': 'notification',
            }
        }
        msg = ''
        if changed_field == 'cv_sex_updated_date' and self.cv_sex_updated_date:
            today = fields.Date.from_string(fields.Date.today())
            if fields.Date.from_string(self.cv_sex_updated_date) > today:
                msg = _('La Fecha de información sexo no puede ser posterior a la fecha actual')
        elif changed_field == 'cv_birthdate' and self.cv_birthdate:
            today = fields.Date.from_string(fields.Date.today())
            if fields.Date.from_string(self.cv_birthdate) > today:
                msg = _('La Fecha de nacimiento no puede ser posterior a la fecha actual')

        if msg:
            result['warning'].update({'message': msg})
        else:
            result = {}
        return result

    @api.model
    def _run_send_inactivity_cv_cron(self):
        """
        Cron que envia la notificación al usuario por período de inactividad en el CV
        :return:
        """
        parameter_inactivity = self.env['ir.config_parameter'].sudo().get_param('parameter_inactivity_cv_value')
        try:
            if int(eval(str(parameter_inactivity))):
                pass
        except Exception:
            raise ValidationError(_("El valor del parámetro de incatividad del CV tiene que ser un número entero"))

        email_template_id = self.env.ref('onsc_cv_digital.email_template_inactivity_cv')
        model_id = self.env['ir.model']._get_id(self._name)
        email_template_id.model_id = model_id
        today = fields.Date.today()
        onsc_cv_digitals = self.env['onsc.cv.digital'].search(
            [('last_modification_date', '!=', False),
             ('type', '=', 'cv'),
             ('last_modification_date', '!=', today)])
        for onsc_cv_digital in onsc_cv_digitals:
            rest_value = today - onsc_cv_digital.last_modification_date
            date_value = int(rest_value.days) % int(parameter_inactivity)
            if not date_value:
                months = diff_month(today, onsc_cv_digital.last_modification_date)
                view_context = dict(self._context)
                view_context.update({
                    'months': months,
                })
                email_template_id.with_context(view_context).send_mail(onsc_cv_digital.id, force_send=True,
                                                                       notif_layout='mail.mail_notification_light')

    def _check_todisable(self):
        for record in self:
            if record._check_todisable_dynamic_fields():
                raise ValidationError(_("No es posible inactivar su CV porque tiene o tuvo "
                                        "algún vínculo laboral con el Estado"))
        return True

    def _check_todisable_dynamic_fields(self):
        return self._is_rve_link()

    def _get_documentary_validation_state(self):
        # TODO este metodo debe retornar el estado final de la validacion documental de todo el CV
        return 'to_validate'

    def _is_rve_link(self):
        if not self.env.user.company_id.is_rve_integrated:
            return False
        response = self._response_connect(self)
        if isinstance(response, str):
            raise ValidationError(_(u"Error en la integración con RVE: " + response))
        try:
            cv_with_rve_link_active = response.Tiene_vinculo_laboral_actual
            cv_with_rve_link_inactive = response.Tuvo_vinculo_laboral
            if cv_with_rve_link_active is not None and cv_with_rve_link_active.upper() == 'S':
                return True
            elif cv_with_rve_link_inactive is not None and cv_with_rve_link_inactive.upper() == 'S':
                return True
            else:
                return False
        except Exception:
            raise ValidationError(_(u"Ha ocurrido un error en la validación con RVE. "
                                    u"Por favor contacte al administrador"))

    def _response_connect(self, obj):
        # TODO check con RVE
        wsdl = self.env.user.company_id.rve_wsdl
        client = Client(wsdl)
        paisCod = obj.cv_emissor_country_id.code_rve
        tipoDoc = obj.cv_document_type_id.code_other
        numDoc = obj.cv_nro_doc
        try:
            response = client.service.Execute(Paiscod=paisCod, Tipodoc=tipoDoc, Numdoc=numDoc)
            # _logger.info("XML respuesta :" + etree_to_string(response).decode())
            return response
        except Fault as fault:
            formatted_response = fault
        except IOError:
            formatted_response = "Servidor no encontrado."
        return formatted_response

    @api.model
    def create(self, values):
        record = super(ONSCCVDigital, self).create(values)
        if values.get('cv_address_street_id'):
            record.partner_id.suspend_security().write(
                {'street': record.cv_address_street_id.street, 'street2': record.cv_address_street2_id.street,
                 'cv_street3': record.cv_address_street3_id.street})
        return record

    def write(self, values):
        records = super(ONSCCVDigital, self).write(values)
        self.update_header_documentary_validation(values)
        if values.get('country_code') == 'UY' or values.get('cv_address_street_id') or values.get(
                'cv_address_street2_id') or values.get('cv_address_street3_id'):
            for record in self:
                record.partner_id.suspend_security().write(
                    {'street': record.cv_address_street_id.street, 'street2': record.cv_address_street2_id.street,
                     'cv_street3': record.cv_address_street3_id.street})
        else:
            self.filtered(lambda x: x.country_code != 'UY').mapped('partner_id').suspend_security().write({
                'street2': False,
                'cv_street3': False
            })
        return records

    def update_header_documentary_validation(self, values):
        cv_expiration_date_value = values.get('cv_expiration_date')
        document_identity_file_value = values.get('document_identity_file')
        civical_credential_file_value = values.get('civical_credential_file')
        crendencial_serie_value = values.get('crendencial_serie')
        credential_number_value = values.get('credential_number')
        document_certificate_file_value = values.get('document_certificate_file')
        certificate_date_file_value = values.get('certificate_date')
        to_date_file_value = values.get('to_date')
        if cv_expiration_date_value or document_identity_file_value:
            self.nro_doc_write_date = fields.Datetime.now()
            self.nro_doc_documentary_validation_state = 'to_validate'
        if civical_credential_file_value or crendencial_serie_value or credential_number_value:
            self.civical_credential_write_date = fields.Datetime.now()
            self.civical_credential_documentary_validation_state = 'to_validate'
        if document_certificate_file_value or certificate_date_file_value or to_date_file_value:
            self.disabilitie_write_date = fields.Datetime.now()
            self.disabilitie_documentary_validation_state = 'to_validate'
            
    def _get_report_cv_formation_seccion(self):
        result = {}
        report_cv_seccions = []
        formations = self.advanced_formation_ids
        seccions = formations.mapped('advanced_study_level_id')
        seccions = sorted(seccions, key=lambda x: x.report_cv_order)
        for seccion in seccions:
            if seccion.report_cv_seccion not in report_cv_seccions:
                result[seccion.report_cv_seccion] = formations.filtered(lambda x: x.advanced_study_level_id.report_cv_seccion == seccion.report_cv_seccion)
                report_cv_seccions.append(seccion.report_cv_seccion)
        return result


class ONSCCVOtherRelevantInformation(models.Model):
    _name = 'onsc.cv.other.relevant.information'
    _inherit = 'onsc.cv.abstract.documentary.validation'
    _description = 'Otra información relevante'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string=u"CV", index=True, ondelete='cascade', required=True)
    theme = fields.Char(string=u"Tema")
    description = fields.Text(string=u"Descripción")

    def _get_json_dict(self):
        json_dict = super(ONSCCVOtherRelevantInformation, self)._get_json_dict()
        json_dict.extend([
            "theme",
            "description",
        ])
        return json_dict
