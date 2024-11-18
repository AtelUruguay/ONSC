# -*- coding: utf-8 -*-

import json
import logging
import zipfile
from os import remove
from os.path import join

from odoo.addons.onsc_base.soap import soap_error_codes as onsc_error_codes

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from .abstracts.onsc_cv_abstract_common import SELECTION_RADIO
from .abstracts.onsc_cv_abstract_config import STATES as CONDITIONAL_VALIDATION_STATES
from .abstracts.onsc_cv_abstract_documentary_validation import DOCUMENTARY_VALIDATION_STATES
from ..soap import soap_error_codes

_logger = logging.getLogger(__name__)


class ONSCCVDigitalCall(models.Model):
    _name = 'onsc.cv.digital.call'
    _inherits = {'onsc.cv.digital': 'cv_digital_id'}
    _description = 'Llamado'
    _rec_name = 'cv_full_name'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_call_documentary_validation') and self.env.user.has_group(
                'onsc_cv_digital.group_validador_documental_cv'):
            args = expression.AND([[
                ('partner_id', '!=', self.env.user.partner_id.id),
            ], args])
        if self._context.get('is_mypostulations') and not self._context.get('from_cv_action'):
            args = expression.AND([[
                ('type', '=', 'call'),
                ('cv_digital_origin_id.partner_id', 'in', [self.env.user.partner_id.id]),
            ], args])

        return super(ONSCCVDigitalCall, self)._search(
            args, offset=offset, limit=limit, order=order,
            count=count,
            access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_call_documentary_validation') and self.env.user.has_group(
                'onsc_cv_digital.group_validador_documental_cv'):
            domain = expression.AND([[
                ('partner_id', '!=', self.env.user.partner_id.id),
            ], domain])
        return super(ONSCCVDigitalCall, self).read_group(
            domain, fields, groupby, offset=offset,
            limit=limit, orderby=orderby,
            lazy=lazy)

    cv_digital_id = fields.Many2one(
        "onsc.cv.digital",
        string="CV interno",
        auto_join=True,
        required=True,
        index=True)

    cv_digital_origin_id = fields.Many2one(
        "onsc.cv.digital",
        string="CV",
        ondelete='set null',
        index=True)

    @api.depends('postulation_date')
    def _compute_postulation_date_str(self):
        for rec in self:
            rec.postulation_date_str = str(rec.postulation_date)

    call_number = fields.Char(string=u"Llamado", required=True, index=True)
    postulation_date = fields.Datetime(string=u"Fecha de actualización", required=True, index=True)
    postulation_date_str = fields.Char(string=u"Fecha de actualización (Texto)",
                                       compute='_compute_postulation_date_str',
                                       store=True)
    postulation_number = fields.Char(string=u"Número de postulación", required=True, index=True)
    is_close = fields.Boolean(string="Cerrado", default=False)
    is_json_sent = fields.Boolean(string="Copia enviada", default=False)
    is_cancel = fields.Boolean(string="Cancelado")
    is_zip = fields.Boolean(string="ZIP generado")
    is_trans = fields.Boolean(string=u"Personas Trans (Art.12 Ley N° 19.684) Cupo")
    is_afro = fields.Boolean(string=u"Afrodescendientes (Art.4 Ley N° 19122) Cupo")
    is_disabilitie = fields.Boolean(string=u"Persona con Discapacidad (Art. 49 Ley N° 18.651) Cupo")
    is_victim = fields.Boolean(string=u"Personas víctimas de delitos violentos (Art. 105 Ley N° 19.889) Cupo")
    preselected = fields.Selection(string="Preseleccionado", selection=[('yes', 'Si'), ('no', 'No')])

    call_conditional_state = fields.Selection(
        string="Estado de valores condicionales",
        selection=CONDITIONAL_VALIDATION_STATES,
        compute='_compute_call_conditional_state', store=True)

    gral_info_documentary_validation_state = fields.Selection(
        selection=DOCUMENTARY_VALIDATION_STATES,
        string="Estado de validación documental general",
        compute='_compute_gral_info_documentary_validation_state',
        store=True
    )

    documentary_validation_sections_tovalidate = fields.Char(
        string="Secciones por validar",
        compute='_compute_gral_info_documentary_validation_state',
        store=True
    )

    show_victim_info = fields.Boolean(string="Mostrar la información de víctimas de delitos violentos", compute='_compute_show_victim_info')
    show_race_info = fields.Boolean(string="Mostrar la información de raza", compute='_compute_show_race_info')
    show_disabilitie_info = fields.Boolean(string="Mostrar la información de discapacidad", compute='_compute_show_disabilitie_info')
    show_gender_info = fields.Boolean(compute='_compute_show_gender_info')

    @api.constrains("cv_digital_id", "cv_digital_id.active", "call_number", "cv_digital_origin_id")
    def _check_cv_call_unicity(self):
        for record in self.filtered(lambda x: x.active):
            if self.search_count([('active', '=', True),
                                  ('cv_digital_origin_id', '=', record.cv_digital_origin_id.id),
                                  ('call_number', '=', record.call_number),
                                  ('id', '!=', record.id)]):
                raise ValidationError(
                    _(u"El CV ya se encuentra activo para este llamado")
                )

    def init(self):
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS onsc_cv_digital_call_postulation_number
                                    ON onsc_cv_digital_call (call_number,postulation_number)
        """)

    @api.depends(
        'cv_address_state',
        'basic_formation_ids.conditional_validation_state',
        'advanced_formation_ids.conditional_validation_state',
        'course_ids.conditional_validation_state',
        'certificate_ids.conditional_validation_state',
        'work_experience_ids.conditional_validation_state',
        'work_teaching_ids.conditional_validation_state',
        'work_investigation_ids.conditional_validation_state',
        'tutoring_orientation_supervision_ids.conditional_validation_state',
        'participation_event_ids.conditional_validation_state',
    )
    def _compute_call_conditional_state(self):
        # FIXME codigo sql es mas optimo pero no cubre todas las casuisticas(creacion todavia no esta en base de datos), se pasa a python
        # pylint: disable=sql-injection
        for record in self.filtered(lambda x: x.is_json_sent is False and x.active):
            conditional_validation_state = record.course_certificate_ids.mapped('conditional_validation_state')
            conditional_validation_state.extend(record.participation_event_ids.mapped('conditional_validation_state'))
            conditional_validation_state.extend(record.work_experience_ids.mapped('conditional_validation_state'))
            conditional_validation_state.extend(record.basic_formation_ids.mapped('conditional_validation_state'))
            conditional_validation_state.extend(record.advanced_formation_ids.mapped('conditional_validation_state'))
            conditional_validation_state.extend(record.work_teaching_ids.mapped('conditional_validation_state'))
            conditional_validation_state.extend(record.work_investigation_ids.mapped('conditional_validation_state'))
            conditional_validation_state.extend(record.participation_event_ids.mapped('conditional_validation_state'))
            conditional_validation_state.append(record.cv_address_state)
            if 'to_validate' in conditional_validation_state:
                record.call_conditional_state = 'to_validate'
            else:
                record.call_conditional_state = 'validated'

    def _get_documentary_validation_models(self, only_fields=False):
        try:
            configs = self.env['onsc.cv.documentary.validation.config'].get_config()
            if only_fields:
                validation_models = []
                for config in configs.filtered(lambda x: x.field_id):
                    validation_models.append('%s' % config.field_id.name)
            else:
                validation_models = ['civical_credential_documentary_validation_state',
                                     'nro_doc_documentary_validation_state',
                                     'disabilitie_documentary_validation_state']
                for config in configs.filtered(lambda x: x.field_id):
                    if config.model_id.model == 'onsc.cv.course.certificate':
                        validation_models.extend(['course_ids.documentary_validation_state',
                                                  'certificate_ids.documentary_validation_state'])
                    else:
                        validation_models.append('%s.documentary_validation_state' % config.field_id.name)
        except Exception:
            validation_models = [
                'civical_credential_documentary_validation_state',
                'nro_doc_documentary_validation_state',
                'disabilitie_documentary_validation_state'
            ]
        return validation_models

    @api.depends(lambda self: self._get_documentary_validation_models())
    def _compute_gral_info_documentary_validation_state(self):
        field_documentary_validation_models = self._get_documentary_validation_models()
        for record in self.filtered(lambda x: x.is_zip is False):
            sections_tovalidate = []
            for documentary_validation_model in field_documentary_validation_models:
                documentary_states = eval("record.mapped('%s')" % documentary_validation_model)
                if len(documentary_states) and 'to_validate' in documentary_states:
                    documentary_validation_model_split = documentary_validation_model.split('.')
                    if len(documentary_validation_model_split) == 2:
                        sections_tovalidate.append(
                            eval("record.%s._description" % documentary_validation_model_split[0]))
                    elif documentary_validation_model == 'civical_credential_documentary_validation_state' and record.is_civical_credential_populated:
                        sections_tovalidate.append(_('Credencial cívica'))
                    elif documentary_validation_model == 'nro_doc_documentary_validation_state':
                        sections_tovalidate.append(_('Documento de identidad'))
                    elif documentary_validation_model == 'disabilitie_documentary_validation_state' and record.show_disabilitie_info and record.situation_disability == 'si':
                        sections_tovalidate.append(_('Discapacidad'))
            if len(sections_tovalidate) > 0:
                documentary_validation_state = 'to_validate'
            else:
                documentary_validation_state = 'validated'
            record.gral_info_documentary_validation_state = documentary_validation_state
            sections_tovalidate = list(dict.fromkeys(sections_tovalidate))
            sections_tovalidate.sort()
            record.documentary_validation_sections_tovalidate = ', '.join(sections_tovalidate)

    def _compute_show_victim_info(self):
        conditional_show = self._context.get('is_call_documentary_validation', False)
        for record in self:
            first_condition = conditional_show and record.is_public_information_victim_violent or record.is_victim_violent
            record.show_victim_info = first_condition or not conditional_show

    def _compute_show_race_info(self):
        conditional_show = self._context.get('is_call_documentary_validation', False)
        for record in self:
            _first_condition = record.is_cv_race_public or record.is_afro
            first_condition = conditional_show and _first_condition and record.is_afro_descendants
            record.show_race_info = first_condition or not conditional_show

    def _compute_show_disabilitie_info(self):
        conditional_show = self._context.get('is_call_documentary_validation', False)
        for record in self:
            _disabilitie = record.allow_content_public == 'si' or record.is_disabilitie
            first_condition = conditional_show and _disabilitie and record.people_disabilitie == 'si'
            record.show_disabilitie_info = first_condition or not conditional_show

    def _compute_show_gender_info(self):
        conditional_show = self._context.get('is_call_documentary_validation', False)
        for record in self:
            _first_condition = record.is_cv_gender_public or record.is_trans
            first_condition = conditional_show and _first_condition and record.cv_gender_id.record
            record.show_gender_info = first_condition or not conditional_show

    def button_update_documentary_validation_sections_tovalidate(self):
        self._compute_gral_info_documentary_validation_state()

    def button_documentary_tovalidate(self):
        if self._context.get('documentary_validation'):
            self._update_documentary(self._context.get('documentary_validation'), 'to_validate', '')

    def button_documentary_approve(self):
        if self._context.get('documentary_validation'):
            self._update_documentary(self._context.get('documentary_validation'), 'validated', '')

    def button_documentary_reject(self):
        if self.filtered(lambda x: x.is_zip):
            raise ValidationError(_("No se puede rechazar Copias de CV si tiene el ZIP generado!"))
        ctx = self._context.copy()
        ctx.update({
            'default_model_name': self._name,
            'default_res_id': len(self.ids) == 1 and self.id or 0,
            'is_documentary_reject': True
        })
        if ctx.get('tree_view_ref'):
            ctx.pop('tree_view_ref')
        if ctx.get('form_view_ref'):
            ctx.pop('form_view_ref')
        return {
            'name': _('Rechazo de %s' % self._description),
            'view_mode': 'form',
            'res_model': 'onsc.cv.reject.wizard',
            'target': 'new',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    def documentary_reject(self, reject_reason):
        if self._context.get('documentary_validation'):
            self._update_documentary(self._context.get('documentary_validation'), 'rejected', reject_reason)
        elif self._context.get('massive_documentary_reject'):
            self.massive_documentary_reject(reject_reason)

    def massive_documentary_reject(self, reject_reason):
        today = fields.Date.today()
        user_id = self.env.user.id
        self.write({
            'disabilitie_documentary_validation_state': 'rejected',
            'nro_doc_documentary_validation_state': 'rejected',
            'civical_credential_documentary_validation_state': 'rejected',
            'disabilitie_documentary_reject_reason': reject_reason,
            'nro_doc_documentary_reject_reason': reject_reason,
            'civical_credential_documentary_reject_reason': reject_reason,
            'disabilitie_documentary_validation_date': today,
            'nro_doc_documentary_validation_date': today,
            'civical_credential_documentary_validation_date': today,
            'disabilitie_documentary_user_id': user_id,
            'nro_doc_documentary_user_id': user_id,
            'civical_credential_documentary_user_id': user_id,
        })
        validation_childs = self._get_documentary_validation_models(only_fields=True)
        if 'certificate_ids' in validation_childs:
            validation_childs.append('course_ids')
        for validation_child in validation_childs:
            self.mapped(validation_child).documentary_reject(reject_reason)

    def _update_documentary(self, documentary_field, state, reject_reason):
        vals = {
            '%s_documentary_validation_state' % documentary_field: state,
            '%s_documentary_reject_reason' % documentary_field: reject_reason,
            '%s_documentary_validation_date' % documentary_field: fields.Date.today(),
            '%s_documentary_user_id' % documentary_field: self.env.user.id,
        }
        self.write(vals)
        self._update_cv_digital_origin_documentary_values(documentary_field, vals)

    def _update_cv_digital_origin_documentary_values(self, documentary_field, vals):
        for record in self:
            cv_digital_origin_id = record.cv_digital_origin_id
            if cv_digital_origin_id and eval(
                    'cv_digital_origin_id.%s_write_date' % documentary_field) < record.create_date:
                cv_digital_origin_id.write(vals)

    def test_json(self):
        self.send_notification_document_validators(self.call_number)

    def _generate_json(self, call_number):
        call_server_json_url = self.env.user.company_id.call_server_json_url
        if call_server_json_url is False:
            return False
        if self.filtered(lambda x: x.call_conditional_state != 'validated'):
            self.send_notification_conditional(call_number)
            return False
        call_number = call_number.replace('/', '_')
        filename = '%s_%s.json' % (call_number, str(fields.Datetime.now()))
        json_file = open(join(call_server_json_url, filename), 'w')
        for record in self:
            json.dump(record._get_json(), json_file)
        self.write({
            'is_json_sent': True
        })

    def generate_zip(self):
        pdf_list = {}
        cv_zip_url = self.env.user.company_id.cv_zip_url
        if len(self) == 0 or not cv_zip_url:
            raise ValidationError(
                _("No se ha podido identificar una ruta en el servidor para almacenar el ZIP. Contacte al administrador."))
        if self.filtered(lambda x: x.gral_info_documentary_validation_state != 'validated'):
            raise ValidationError(_("No se puede generar ZIP si no están validados documentalmente"))
        if len(list(dict.fromkeys(self.mapped('call_number')))) > 1:
            raise ValidationError(_("No se puede generar ZIP de CVs de diferentes llamados"))
        try:
            self = self.with_context(is_call_documentary_validation=True, cv_digital_call=True)
            wizard = self.env['onsc.cv.report.wizard'].create({})
            call_number = self[0].call_number.replace('/', '_')
            for record in self:
                report = self.env.ref('onsc_cv_digital.action_report_onsc_cv_digital').with_context(
                    seccions=wizard.get_seccions())._render_qweb_pdf(record.cv_digital_id.id)
                pdfname = '%s_%s_%s.pdf' % (call_number,
                                            record.postulation_number,
                                            str(fields.Datetime.now().strftime('%Y-%m-%d %H-%M-%S')))
                pdf_url = join(cv_zip_url, pdfname)
                thePdf = open(pdf_url, 'wb')
                thePdf.write(report[0])
                pdf_list[pdfname] = pdf_url
                thePdf.close()
            filename = '%s_%s.zip' % (call_number, str(fields.Datetime.now().strftime('%Y-%m-%d %H-%M-%S')))
            cv_zip_url = join(cv_zip_url, filename)
            zip_archive = zipfile.ZipFile(cv_zip_url, "w")
            try:
                compression = zipfile.ZIP_DEFLATED
            except Exception:
                compression = zipfile.ZIP_STORED
            try:
                for pdfname, pdf_url in pdf_list.items():
                    zip_archive.write(pdf_url, arcname=pdfname, compress_type=compression)
                    remove(pdf_url)
            finally:
                zip_archive.close()
        except Exception:
            raise ValidationError(_("No se ha podido generar el ZIP. Contacte con el administrador"))
        self.write({'is_zip': True})
        return True

    @api.model
    def create(self, values):
        values['type'] = 'call'
        return super(ONSCCVDigitalCall, self).create(values)

    # -------------------------------------------------------------------------------------------------------------------
    #   WS utilities
    # -------------------------------------------------------------------------------------------------------------------
    def _get_json(self):
        return self.jsonify(self._get_json_dict())

    def _get_json_dict(self):
        # JSONifier
        race_json = self.env['onsc.cv.race']._get_json_dict()
        driver_license_json = self.env['onsc.cv.driver.license']._get_json_dict()
        # Formación----<Page>
        advanced_formation_json = self.env['onsc.cv.advanced.formation']._get_json_dict()
        basic_formation_json = self.env['onsc.cv.basic.formation']._get_json_dict()

        # Cursos y certificado----<Page>
        course_json = self.env['onsc.cv.course.certificate']._get_json_dict()
        certificate_json = course_json

        # Experiencia Laboral ----<Page>
        work_experience_json = self.env['onsc.cv.work.experience']._get_json_dict()

        # Docencia ----<Page>
        work_teaching_json = self.env['onsc.cv.work.teaching']._get_json_dict()

        # Investigación ----<Page>
        work_investigation_json = self.env['onsc.cv.work.investigation']._get_json_dict()

        # Voluntariado ----<Page>
        volunteering_json = self.env['onsc.cv.volunteering']._get_json_dict()

        # Idioma ----<Page>
        language_level_json = self.env['onsc.cv.language.level']._get_json_dict()

        # Publicaciones, Producciones y Evaluaciones ----<Page>
        publication_production_evaluation_json = self.env['onsc.cv.publication.production.evaluation']._get_json_dict()

        # Tutorías, Orientaciones, Supervisiones ----<Page>
        tutoring_orientation_supervision_json = self.env['onsc.cv.tutoring.orientation.supervision']._get_json_dict()

        # Participación en Eventos ----<Page>
        participation_event_json = self.env['onsc.cv.participation.event']._get_json_dict()
        # Otra información relevante ----<Page>
        other_relevant_information_json = self.env['onsc.cv.other.relevant.information']._get_json_dict()
        # Referencias ------<Page>
        reference_json = self.env['onsc.cv.reference']._get_json_dict()
        # Tipos de apoyo ------<Page>
        type_support_json = self.env['onsc.cv.type.support']._get_json_dict()

        parser = [
            'id',
            'active',
            'create_date',
            'create_uid',
            'write_date',
            'write_uid',
            'cv_full_name',
            'call_number',
            'postulation_date',
            'postulation_number',
            'preselected',
            'is_trans',
            'is_afro',
            'is_disabilitie',
            'is_victim',
            ("cv_emissor_country_id", ["id", "name"]),
            ("cv_document_type_id", ["id", "name"]),
            'cv_nro_doc',
            'identity_document_expiration_date',
            'email',
            'cv_birthdate',
            # 'image_1920',
            # Domicilio
            ("country_id", ["id", "name"]),
            ("cv_address_state_id", ["id", "name"]),
            ("cv_address_location_id", ["id", "name"]),
            ("cv_address_street_id", ["id", "street"]),
            ("cv_address_street2_id", ["id", "street"]),
            ("cv_address_street3_id", ["id", "street"]),
            'cv_address_nro_door',
            'cv_address_apto',
            'cv_address_street',
            'cv_address_zip',
            'cv_address_is_cv_bis',
            'cv_address_amplification',
            'cv_address_state',
            'cv_address_reject_reason',
            'cv_address_place',
            'cv_address_block',
            'cv_address_sandlot',
            ("country_of_birth_id", ["id", "name"]),
            'uy_citizenship',
            # Datos personales
            ("marital_status_id", ["id", "name"]),
            'crendencial_serie',
            'credential_number',
            'cjppu_affiliate_number',
            'professional_resume',
            'user_linkedIn',
            'is_driver_license',
            'prefix_phone_id',
            'personal_phone',
            'prefix_mobile_phone_id',
            'mobile_phone',
            'is_occupational_health_card',
            'occupational_health_card_date',
            'is_medical_aptitude_certificate_status',
            'medical_aptitude_certificate_date',
            'civical_credential_documentary_validation_state',
            'civical_credential_documentary_reject_reason',
            'civical_credential_documentary_user_id',
            'civical_credential_documentary_validation_date',
            'disabilitie_documentary_validation_state',
            'disabilitie_documentary_reject_reason',
            'disabilitie_documentary_user_id',
            'disabilitie_documentary_validation_date',
            'nro_doc_documentary_validation_state',
            'nro_doc_documentary_reject_reason',
            'nro_doc_documentary_user_id',
            'nro_doc_documentary_validation_date',
        ]
        if self.with_context(is_call_documentary_validation=True).show_race_info:
            parser.extend(['cv_race2',
                           ('cv_first_race_id', ['id', 'name']),
                           'is_cv_race_public',
                           'is_afro_descendants',
                           ('cv_race_ids', race_json)])
        if self.with_context(is_call_documentary_validation=True).show_gender_info:
            parser.extend(['last_modification_date',
                           ('cv_gender_id', ['id', 'name']),
                           'cv_gender2',
                           'is_cv_gender_public'])
        if self.with_context(is_call_documentary_validation=True).show_victim_info:
            parser.extend(['is_victim_violent',
                           'is_public_information_victim_violent'])
        if self.with_context(is_call_documentary_validation=True).show_disabilitie_info:
            parser.extend(['allow_content_public',
                           'situation_disability',
                           'people_disabilitie',
                           'certificate_date',
                           'to_date',
                           ('walk', lambda self, field_name: self.parser_selection_tovalue('walk')),
                           ('see', lambda self, field_name: self.parser_selection_tovalue('see')),
                           ('hear', lambda self, field_name: self.parser_selection_tovalue('hear')),
                           ('speak', lambda self, field_name: self.parser_selection_tovalue('speak')),
                           ('realize', lambda self, field_name: self.parser_selection_tovalue('realize')),
                           ('lear', lambda self, field_name: self.parser_selection_tovalue('lear')),
                           ('interaction', lambda self, field_name: self.parser_selection_tovalue('interaction')),
                           'need_other_support',
                           ('type_support_ids', type_support_json), ])
        parser.extend([
            ('drivers_license_ids', driver_license_json),
            ('basic_formation_ids', basic_formation_json),
            ('advanced_formation_ids', advanced_formation_json),
            ('course_ids', course_json),
            ('certificate_ids', certificate_json),
            ('work_experience_ids', work_experience_json),
            ('work_teaching_ids', work_teaching_json),
            ('work_investigation_ids', work_investigation_json),
            ('volunteering_ids', volunteering_json),
            ('language_level_ids', language_level_json),
            ('publication_production_evaluation_ids', publication_production_evaluation_json),
            ('tutoring_orientation_supervision_ids', tutoring_orientation_supervision_json),
            ('participation_event_ids', participation_event_json),
            ('other_relevant_information_ids', other_relevant_information_json),
            ('reference_ids', reference_json),
        ])
        return parser

    def parser_selection_tovalue(self, field_name):
        return dict(SELECTION_RADIO).get(eval('self.%s' % field_name))

    def action_get_json_dict(self):
        _logger.debug(self._get_json())

    @api.model
    def _run_call_json_cron(self):
        """
        Cron que envia la notificación al usuario por período de inactividad en el CV
        :return:
        """
        self.env.cr.execute(
            '''SELECT DISTINCT(call_number) FROM onsc_cv_digital_call call WHERE call.is_close is True AND call.is_json_sent is False''')
        results = self.env.cr.dictfetchall()
        for result in results:
            call_number = result.get('call_number')
            calls = self.search([('call_number', '=', call_number)])
            if len(calls):
                calls._generate_json(call_number)

    # WS Postulacion
    @api.model
    def create_postulation(self,
                           country_code,
                           doc_type_code,
                           doc_number,
                           postulation_date,
                           postulation_number,
                           call_number,
                           accion,
                           ):
        """

        :param country_code:
        :param doc_type_code:
        :param doc_number:
        :param postulation_date:
        :param postulation_number:
        :param call_number:
        :param accion:
        :return:
        """
        if len(country_code) != 2:
            return onsc_error_codes._raise_fault(soap_error_codes.LOGIC_151_1)
        country_id = self.env['res.country'].search([('code', '=', country_code)], limit=1)
        if not country_id:
            return onsc_error_codes._raise_fault(soap_error_codes.LOGIC_151)
        doc_type_id = self.env['onsc.cv.document.type'].search([('code', '=', doc_type_code)], limit=1)
        if not doc_type_id:
            return onsc_error_codes._raise_fault(soap_error_codes.LOGIC_152)
        if not isinstance(accion, str) or accion not in ['P', 'R', 'C']:
            return onsc_error_codes._raise_fault(soap_error_codes.LOGIC_154)

        cv_digital_id = self.env['onsc.cv.digital'].search([
            ('cv_emissor_country_id', '=', country_id.id),
            ('cv_document_type_id', '=', doc_type_id.id),
            ('cv_nro_doc', '=', doc_number),
            ('type', '=', 'cv')
        ], limit=1)
        if not cv_digital_id:
            return onsc_error_codes._raise_fault(soap_error_codes.LOGIC_153)

        if accion == 'P':
            return self._postulate(cv_digital_id, call_number, postulation_date, postulation_number)
        elif accion == 'R':
            return self._repostulate(cv_digital_id, call_number, postulation_date, postulation_number)
        elif accion == 'C':
            return self._cancel_postulation(cv_digital_id, call_number, postulation_date)
        return True

    def _postulate(self, cv_digital_id, call_number, postulation_date, postulation_number):
        new_cv_digital = cv_digital_id.copy({
            'type': 'call',
            'document_identity_file': cv_digital_id.document_identity_file,
            'document_identity_filename': cv_digital_id.document_identity_filename,
            'country_of_birth_id': cv_digital_id.country_of_birth_id.id,
            'marital_status_id': cv_digital_id.marital_status_id.id,
            'uy_citizenship': cv_digital_id.uy_citizenship,
            'crendencial_serie': cv_digital_id.crendencial_serie,
            'credential_number': cv_digital_id.credential_number,
            'civical_credential_file': cv_digital_id.civical_credential_file,
            'civical_credential_filename': cv_digital_id.civical_credential_filename,
            'cjppu_affiliate_number': cv_digital_id.cjppu_affiliate_number,
            'professional_resume': cv_digital_id.professional_resume,
            'user_linkedIn': cv_digital_id.user_linkedIn,
            'is_driver_license': cv_digital_id.is_driver_license,
            'cv_gender_id': cv_digital_id.cv_gender_id.id,
            'cv_gender2': cv_digital_id.cv_gender2,
            'cv_gender_record_file': cv_digital_id.cv_gender_record_file,
            'cv_gender_record_filename': cv_digital_id.cv_gender_record_filename,
            'is_cv_gender_public': cv_digital_id.is_cv_gender_public,
            'is_cv_gender_record': cv_digital_id.is_cv_gender_record,
            'cv_race2': cv_digital_id.cv_race2,
            'is_cv_race_public': cv_digital_id.is_cv_race_public,
            'is_afro_descendants': cv_digital_id.is_afro_descendants,
            'afro_descendants_file': cv_digital_id.afro_descendants_file,
            'afro_descendants_filename': cv_digital_id.afro_descendants_filename,
            'is_occupational_health_card': cv_digital_id.is_occupational_health_card,
            'occupational_health_card_date': cv_digital_id.occupational_health_card_date,
            'occupational_health_card_file': cv_digital_id.occupational_health_card_file,
            'occupational_health_card_filename': cv_digital_id.occupational_health_card_filename,
            'is_medical_aptitude_certificate_status': cv_digital_id.is_medical_aptitude_certificate_status,
            'medical_aptitude_certificate_date': cv_digital_id.medical_aptitude_certificate_date,
            'medical_aptitude_certificate_file': cv_digital_id.medical_aptitude_certificate_file,
            'medical_aptitude_certificate_filename': cv_digital_id.medical_aptitude_certificate_filename,
            'is_victim_violent': cv_digital_id.is_victim_violent,
            'relationship_victim_violent_file': cv_digital_id.relationship_victim_violent_file,
            'relationship_victim_violent_filename': cv_digital_id.relationship_victim_violent_filename,
            'is_public_information_victim_violent': cv_digital_id.is_public_information_victim_violent,
            'cv_address_street_id': cv_digital_id.cv_address_street_id.id,
            'cv_address_street2_id': cv_digital_id.cv_address_street2_id.id,
            'cv_address_street3_id': cv_digital_id.cv_address_street3_id.id,
            'allow_content_public': cv_digital_id.allow_content_public,
            'situation_disability': cv_digital_id.situation_disability,
            'people_disabilitie': cv_digital_id.people_disabilitie,
            'document_certificate_file': cv_digital_id.document_certificate_file,
            'document_certificate_filename': cv_digital_id.document_certificate_filename,
            'certificate_date': cv_digital_id.certificate_date,
            'to_date': cv_digital_id.to_date,
            'see': cv_digital_id.see,
            'hear': cv_digital_id.hear,
            'walk': cv_digital_id.walk,
            'speak': cv_digital_id.speak,
            'realize': cv_digital_id.realize,
            'lear': cv_digital_id.lear,
            'interaction': cv_digital_id.interaction,
            'need_other_support': cv_digital_id.need_other_support,
        })
        cv_call = self.env['onsc.cv.digital.call'].create({
            'cv_digital_id': new_cv_digital.id,
            'cv_digital_origin_id': cv_digital_id.id,
            'call_number': call_number,
            'postulation_date': postulation_date,
            'postulation_number': postulation_number,
            'identity_document_expiration_date': cv_digital_id.cv_expiration_date,
        })
        return cv_call

    def _repostulate(self, cv_digital_id, call_number, postulation_date, postulation_number):
        cv_calls = self.search([
            ('cv_digital_origin_id', '=', cv_digital_id.id),
            ('call_number', '=', call_number),
        ])
        if not cv_calls:
            return onsc_error_codes._raise_fault(soap_error_codes.LOGIC_155)
        cv_calls.write({'active': False, 'postulation_date': postulation_date})
        return self._postulate(cv_digital_id, call_number, postulation_date, postulation_number)

    def _cancel_postulation(self, cv_digital_id, call_number, postulation_date):
        cv_calls = self.search([
            ('cv_digital_origin_id', '=', cv_digital_id.id),
            ('call_number', '=', call_number),
        ])
        if not cv_calls:
            return onsc_error_codes._raise_fault(soap_error_codes.LOGIC_155)
        cv_calls.write({'active': False, 'is_cancel': True, 'postulation_date': postulation_date})
        return cv_calls

    # WS Cierre de llamado
    @api.model
    def call_close(self,
                   call_number,
                   operating_number_code,
                   is_trans,
                   is_afro,
                   is_disabilitie,
                   is_victim,
                   ):
        """

        :param call_number:
        :param operating_number_code:
        :param is_trans:
        :param is_afro:
        :param is_disabilitie:
        :param is_victim:
        :return:
        """
        calls = self.search([('call_number', '=', call_number)])
        if len(calls) == 0:
            return onsc_error_codes._raise_fault(soap_error_codes.LOGIC_156)
        if calls[0].is_close:
            return onsc_error_codes._raise_fault(soap_error_codes.LOGIC_157)
        if calls[0].is_json_sent:
            return onsc_error_codes._raise_fault(soap_error_codes.LOGIC_158)
        calls.write(
            self._get_call_close_vals(operating_number_code, is_trans, is_afro, is_disabilitie, is_victim))
        calls._generate_json(call_number)
        return True

    def _get_call_close_vals(self,
                             operating_number_code,
                             is_trans,
                             is_afro,
                             is_disabilitie,
                             is_victim):
        return {
            'is_trans': is_trans,
            'is_afro': is_afro,
            'is_disabilitie': is_disabilitie,
            'is_victim': is_victim,
            'is_close': True
        }

    # WS Datos de llamado
    @api.model
    def call_preselection(self, call_number, postulations):
        """

        :param call_number:
        :param postulations:
        :return:
        """
        calls_preselected = self.search([('call_number', '=', call_number), ('postulation_number', 'in', postulations)])
        calls_not_selected = self.search([('call_number', '=', call_number), ('id', 'not in', calls_preselected.ids)])
        if len(calls_preselected) == 0:
            return onsc_error_codes._raise_fault(soap_error_codes.LOGIC_156)
        calls_preselected.write({'preselected': 'yes'})
        calls_preselected.with_context(is_preselected=True).button_update_documentary_validation_sections_tovalidate()
        calls_not_selected.write({'preselected': 'no'})
        calls_preselected.send_notification_document_validators(call_number)
        return True

    def _get_mailto_send_notification_document_validators(self):
        return {'email_to': self.env.user_id.partner_id.email}

    def send_notification_document_validators(self, call_number):
        ctx = self.env.context.copy()
        ctx.update({'call': call_number})
        email_values = self._get_mailto_send_notification_document_validators()
        template = self.env.ref('onsc_cv_digital.email_template_document_validators_cv')
        template.with_context(ctx).send_mail(len(self) and self[0].id, email_values=email_values)

    def send_notification_conditional(self, call_number):
        template = self.env.ref('onsc_cv_digital.email_template_conditional_values_cv')
        validador_group = self.env.ref("onsc_cv_digital.group_validador_catalogos_cv")
        users = self.env['res.users'].sudo().search([
            ('groups_id', 'in', [validador_group.id])
        ])
        emailto = ','.join(users.filtered(lambda x: x.partner_id.email).mapped('partner_id.email'))
        template.with_context(call=call_number).send_mail(len(self) and self[0].id, email_values={'email_to': emailto})

    def button_print_cv_copy(self):
        res = {
            'name': 'Imprimir CV',
            'view_mode': 'form',
            'res_model': 'onsc.cv.report.wizard',
            'target': 'new',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': {
                'default_cv_digital_ids': self.cv_digital_id.ids,
                'cv_digital_call': True,
                'is_mypostulations': self._context.get('is_mypostulations', False)
            },
        }
        return res

    def cv_digital_call_print_cv(self):
        active_ids = self._context.get('active_ids', False)
        onsc_cv_digital_ids = self.env['onsc.cv.digital.call'].browse(active_ids)
        onsc_cv_report_wizard = self.env['onsc.cv.report.wizard'].create({
            'cv_digital_ids': onsc_cv_digital_ids.cv_digital_id.ids
        })
        return onsc_cv_report_wizard.with_context(cv_digital_call=True).button_print()

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ONSCCVDigitalCall, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                             submenu=submenu)
        is_call_documentary_validation = self._context.get('is_call_documentary_validation', False)
        toolbar = res.get('toolbar', False)
        if toolbar:
            toolbar_actions = res['toolbar'].get('action')
            actions_exclude = []
            if not is_call_documentary_validation:
                print_action = self.env.ref("onsc_cv_digital.onsc_cv_digital_call_documentary_validation_print_action")
                onsc_cv_digital_call_zip = self.env.ref("onsc_cv_digital.onsc_cv_digital_call_zip")
                onsc_cv_digital_call_massive_documentary_reject = self.env.ref(
                    "onsc_cv_digital.onsc_cv_digital_call_massive_documentary_reject")
                actions_exclude.extend([
                    onsc_cv_digital_call_zip.id,
                    onsc_cv_digital_call_massive_documentary_reject.id,
                    print_action.id
                ])
            else:
                print_action = self.env.ref("onsc_cv_digital.onsc_cv_digital_call_print_action")
                actions_exclude.extend([
                    print_action.id
                ])
            if self._context.get('is_mypostulations'):
                print_action1 = self.env.ref("onsc_cv_digital.onsc_cv_digital_call_print_action")
                print_action2 = self.env.ref("onsc_cv_digital.onsc_cv_digital_call_documentary_validation_print_action")
                actions_exclude.extend([print_action1.id, print_action2.id])
            toolbar_actions = [act for act in toolbar_actions if act['id'] not in actions_exclude]
            res['toolbar']['action'] = toolbar_actions
        return res
