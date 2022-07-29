# -*- coding: utf-8 -*-

from lxml import etree
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

from .onsc_cv_useful_tools import get_onchange_warning_response as cv_warning
from .onsc_cv_useful_tools import is_valid_phone

HTML_HELP = """<a     class="btn btn-outline-dark" target="_blank" title="Enlace a la ayuda"
                            href="%s">
                            <i class="fa fa-question-circle-o" role="img" aria-label="Info"/>Ayuda</a>"""
SELECTION_RADIO = [('1', 'Si, no puede hacerlo'), ('2', 'Si, mucha dificultad'),
                   ('3', 'Si, alguna dificultad '), ('4', 'No tiene dificultad')]
SITUATION = u'Está en situación de discapacidad y/o requieres algún apoyo para cumplir con tus actividades laborales?'
DISABILITE = u'¿Está inscripto en el registro de personas con discapacidad del ministerio de desarrollo social?'


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
    country_id = fields.Many2one(related='partner_id.country_id', readonly=False)
    cv_address_state_id = fields.Many2one(related='partner_id.state_id', readonly=False)
    cv_address_location_id = fields.Many2one(related='partner_id.cv_location_id', readonly=False)
    cv_address_street = fields.Char(related='partner_id.street', readonly=False)
    cv_address_nro_door = fields.Char(related='partner_id.cv_nro_door', readonly=False)
    cv_address_apto = fields.Char(related='partner_id.cv_apto', readonly=False)
    cv_address_street2 = fields.Char(related='partner_id.street2', readonly=False)
    cv_address_street3 = fields.Char(related='partner_id.cv_street3', readonly=False)
    cv_address_zip = fields.Char(related='partner_id.zip', readonly=False)
    cv_address_is_cv_bis = fields.Boolean(related='partner_id.is_cv_bis', readonly=False)
    cv_address_amplification = fields.Text(related='partner_id.cv_amplification', readonly=False)
    cv_address_state = fields.Selection(related='cv_address_location_id.state')
    cv_address_reject_reason = fields.Char(related='cv_address_location_id.reject_reason')

    country_of_birth_id = fields.Many2one("res.country", string="País de nacimiento", required=True)
    uy_citizenship = fields.Selection(string="Ciudadanía uruguaya",
                                      selection=[('legal', 'Legal'), ('natural', 'Natural'),
                                                 ('extranjero', 'Extranjero')], required=True)
    marital_status_id = fields.Many2one("onsc.cv.status.civil", string="Estado civil", required=True)
    crendencial_serie = fields.Char(string="Serie de la credencial", size=3)
    credential_number = fields.Integer(string="Numero de la credencial")
    cjppu_affiliate_number = fields.Integer(string="Numero de afiliado a la CJPPU")
    professional_resume = fields.Text(string="Resumen profesional")
    user_linkedIn = fields.Char(string="Usuario en LinkedIn")
    is_afro_descendants = fields.Boolean(string="Afrodescendientes (Art. 4 Ley N°19.122)")
    afro_descendants_file = fields.Binary(
        string='Documento digitalizado "Declaración de afrodescendencia" / formulario web de declaración jurada de afrodescendencia (Art. 4 Ley N°19.122) ')
    afro_descendants_filename = fields.Char('Nombre del documento digital')
    is_driver_license = fields.Boolean(string="Tiene licencia de conducir")
    drivers_license_ids = fields.One2many("onsc.cv.driver.license",
                                          inverse_name="cv_digital_id", string="Licencias de conducir")

    prefix_phone_id = fields.Many2one(related='partner_id.prefix_phone_id', readonly=False)
    personal_phone = fields.Char(string="Teléfono particular", related='partner_id.phone', readonly=False)
    prefix_mobile_phone_id = fields.Many2one(related='partner_id.prefix_mobile_phone_id', readonly=False)
    mobile_phone = fields.Char(string="Teléfono celular", related='partner_id.mobile', readonly=False)
    email = fields.Char(string="Email", related='partner_id.email')

    is_occupational_health_card = fields.Boolean(string="Carné de salud laboral")
    occupational_health_card_date = fields.Date(string="Fecha de vencimiento del carné de salud laboral")
    occupational_health_card_file = fields.Binary(
        string="Documento digitalizado del carné de salud laboral")
    occupational_health_card_filename = fields.Char('Nombre del documento digital')

    document_identity_file = fields.Binary(string="Documento digitalizado del documento de identidad")
    document_identity_filename = fields.Char('Nombre del documento digital')

    civical_credential_file = fields.Binary(string="Documento digitalizado credencial cívica")
    civical_credential_filename = fields.Char('Nombre del documento digital')
    medical_aptitude_certificate_status = fields.Selection(string="Certificado de aptitud médico-deportiva",
                                                           selection=[('si', 'Si'), ('no', 'No'), ])
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
        string="¿Permite que su información de persona víctima de delitos violentos sea público?", )

    # Formación----<Page>
    basic_formation_ids = fields.One2many('onsc.cv.basic.formation', 'cv_digital_id', string=u'Formación básica')
    advanced_formation_ids = fields.One2many('onsc.cv.advanced.formation', 'cv_digital_id',
                                             string=u'Formación avanzada')
    # Cursos y certificado----<Page>
    course_certificate_ids = fields.One2many('onsc.cv.course.certificate', inverse_name='cv_digital_id',
                                             string="Cursos y certificados")
    course_ids = fields.One2many('onsc.cv.course.certificate', inverse_name='cv_digital_id',
                                 string="Cursos", domain=[('record_type', '=', 'course')])
    certificate_ids = fields.One2many('onsc.cv.course.certificate', inverse_name='cv_digital_id',
                                      string="Certificados", domain=[('record_type', '=', 'certificate')])
    # Experiencia Laboral ----<Page>
    work_experience_ids = fields.One2many("onsc.cv.work.experience", inverse_name="cv_digital_id",
                                          string="Experiencia laboral")
    # Docencia ----<Page>
    work_teaching_ids = fields.One2many('onsc.cv.work.teaching', inverse_name='cv_digital_id', string='Docencia')
    # Investigación ----<Page>
    work_investigation_ids = fields.One2many('onsc.cv.work.investigation', inverse_name='cv_digital_id',
                                             string='Investigación')
    # Voluntariado ----<Page>
    volunteering_ids = fields.One2many("onsc.cv.volunteering", inverse_name="cv_digital_id", string="Voluntariado")
    # Idioma ----<Page>
    language_level_ids = fields.One2many('onsc.cv.language.level', inverse_name='cv_digital_id', string='Idiomas')
    # Publicaciones, Producciones y Evaluaciones ----<Page>
    publication_production_evaluation_ids = fields.One2many("onsc.cv.publication.production.evaluation",
                                                            inverse_name="cv_digital_id",
                                                            string="Publicaciones, producciones y evaluaciones")
    # Tutorías, Orientaciones, Supervisiones ----<Page>
    tutoring_orientation_supervision_ids = fields.One2many('onsc.cv.tutoring.orientation.supervision',
                                                           inverse_name="cv_digital_id",
                                                           string="Tutorías, Orientaciones, Supervisiones")
    # Discapacidad ----<Page>
    allow_content_public = fields.Selection(selection=[('si', u'Si'), ('no', u'No')], default='no', required=True,
                                            string=u'¿Permite que el contenido de esta sección sea público?')
    situation_disability = fields.Selection(selection=[('si', u'Si'), ('no', u'No')], string=SITUATION)
    people_disabilitie = fields.Selection(selection=[('si', u'Si'), ('no', u'No')], string=DISABILITE)
    document_certificate_file = fields.Binary(string=u'Documento digitalizado constancia de inscripción en el RNPcD')
    document_certificate_filename = fields.Char('Nombre del documento Digitalizado')
    certificate_date = fields.Date(string=u'Fecha de certificado')
    to_date = fields.Date(string=u'Fecha hasta')
    see = fields.Selection(selection=SELECTION_RADIO, string=u'Ver, ¿aún si usa anteojos o lentes?')
    hear = fields.Selection(selection=SELECTION_RADIO, string=u'Oír, ¿aún si usa audífono?')
    walk = fields.Selection(selection=SELECTION_RADIO, string=u'¿Caminar o subir escalones?')
    speak = fields.Selection(selection=SELECTION_RADIO, string=u'¿Hablar o comunicarse aun usando lengua de señas?')
    realize = fields.Selection(selection=SELECTION_RADIO,
                               string=u'¿Realizar tareas de cuidado personal como comer, bañarse o vestirse solo?')
    lear = fields.Selection(selection=SELECTION_RADIO, string=u'Entender/ y o aprender?')
    interaction = fields.Selection(selection=SELECTION_RADIO, string=u'Interacciones y/o relaciones interpersonales?')
    type_support_ids = fields.Many2many('onsc.cv.type.support', 'type_support_id', string=u'Tipos de apoyo')
    type_support_ids_domain = fields.Many2many('onsc.cv.type.support', 'type_support_domain_id',
                                               compute='_compute_cv_type_support_domain')
    need_other_support = fields.Char(string=u"¿Necesita otro apoyo?")
    is_need_other_support = fields.Boolean(compute='_compute_cv_type_support_domain')
    # Participación en Eventos ----<Page>
    participation_event_ids = fields.One2many("onsc.cv.participation.event",
                                              inverse_name="cv_digital_id",
                                              string="Participación en eventos")
    # Otra información relevante ----<Page>
    other_relevant_information_ids = fields.One2many("onsc.cv.other.relevant.information",
                                                     inverse_name="cv_digital_id",
                                                     string="Otra información relevante")
    # Referencias ------<Page>
    reference_ids = fields.One2many('onsc.cv.reference', inverse_name='cv_digital_id', string='Referencias')

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

    @api.constrains('cv_sex_updated_date', 'cv_birthdate')
    def _check_valid_dates(self):
        today = fields.Date.from_string(fields.Date.today())
        for record in self:
            if record.cv_sex_updated_date and fields.Date.from_string(record.cv_sex_updated_date) > today:
                raise ValidationError(_("La Fecha de información sexo no puede ser posterior a la fecha actual"))
            if record.cv_birthdate and fields.Date.from_string(record.cv_birthdate) > today:
                raise ValidationError(_("La Fecha de nacimiento no puede ser posterior a la fecha actual"))

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
        result = super().toggle_active()
        if len(self) == 1:
            return self.with_context(my_cv=self)._action_open_user_cv()
        return result

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
                [('partner_id', '=', self.env.user.partner_id.id), ('active', 'in', [False, True])], limit=1)
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
            form_parent_id = self.env['ir.ui.view'].search([('model', '=', self._name), ('type', '=', 'form')], limit=1)
            if form_parent_id:
                arch = form_parent_id.arch
                doc = etree.XML(arch)
                for node_form in doc.xpath("//form"):
                    node_form.set('edit', '0')
                form_id = self.env['ir.ui.view'].create(
                    {'name': '%s.form.readonly' % self._name,
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


class ONSCCVOtherRelevantInformation(models.Model):
    _name = 'onsc.cv.other.relevant.information'
    _description = 'Otra información relevante'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string=u"CV", index=True, ondelete='cascade', required=True)
    theme = fields.Char(string=u"Tema")
    description = fields.Text(string=u"Descripción")
