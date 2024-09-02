# -*- coding: utf-8 -*-

from odoo.addons.onsc_base.onsc_useful_tools import to_timestamp as to_timestamp

from odoo import models, fields

# REPORT UTILITIES
_CUSTOM_ORDER = {
    'active': 1,
    'outgoing_commission': 2,
    'incoming_commission': 3,
    'baja': 4,
    'reserved': 5,
}


class ONSCLegajo(models.Model):
    _inherit = "onsc.legajo"

    cv_digital_id = fields.Many2one(
        comodel_name="onsc.cv.digital",
        related='employee_id.cv_digital_id', store=True)

    # FORMACION

    basic_formation_ids = fields.One2many(
        'onsc.legajo.basic.formation', string=u'Formación básica', inverse_name="legajo_id", )
    advanced_formation_ids = fields.One2many(
        'onsc.legajo.advanced.formation', string=u'Formación avanzada', inverse_name="legajo_id")

    # CURSOS Y CERTIFICADOS
    course_ids = fields.One2many(
        'onsc.legajo.course.certificate',
        string="Cursos", inverse_name="legajo_id")
    certificate_ids = fields.One2many(
        'onsc.cv.course.certificate',
        string="Certificados",
        compute='_compute_formations',
        compute_sudo=True)

    # EXPERIENCIA LABORAL
    work_experience_ids = fields.One2many(
        "onsc.legajo.work.experience",
        inverse_name="legajo_id",
        string="Experiencia laboral"
    )
    # Tutorías, Orientaciones, Supervisiones
    tutoring_orientation_supervision_ids = fields.One2many(
        'onsc.legajo.tutoring.orientation.supervision',
        inverse_name="legajo_id",
        string="Tutorías, Orientaciones, Supervisiones"
    )
    # VOLUNTARIADO
    volunteering_ids = fields.One2many(
        "onsc.legajo.volunteering",
        inverse_name="legajo_id",
        string="Voluntariado"
    )
    # DOCENCIA
    work_teaching_ids = fields.One2many(
        "onsc.legajo.work.teaching",
        inverse_name="legajo_id",
        string="Docencia"
    )
    # PARTICIPACION EN EVENTOS
    participation_event_ids = fields.One2many(
        "onsc.legajo.participation.event",
        inverse_name="legajo_id",
        string="Participación en eventos"
    )

    # Investigacion
    work_investigation_ids = fields.One2many(
        "onsc.legajo.work.investigation",
        inverse_name="legajo_id",
        string="Investigación"
    )

    # Tutorías, Orientaciones, Supervisiones
    publication_production_evaluation_ids = fields.One2many(
        "onsc.legajo.publication.production.evaluation",
        inverse_name="legajo_id",
        string="Publicación, Producción y Evaluación"
    )
    # Otra Informacion
    other_relevant_information_ids = fields.One2many(
        "onsc.legajo.relevant.information",
        inverse_name="legajo_id",
        string="Otra información relevante"
    )

    is_user_available_to_print_legajo = fields.Boolean(
        string='¿Impresión de Legajo disponible para el usuario?',
        compute='_compute_is_user_available_to_print_legajo'
    )

    def _compute_is_user_available_to_print_legajo(self):
        is_user_valid = self.env.user.has_group('onsc_cv_digital_legajo.group_legajo_reporte_legajo')
        for record in self:
            record.is_user_available_to_print_legajo = is_user_valid or self._context.get('mi_legajo', False)

    def _compute_formations(self):
        for record in self:
            record.certificate_ids = record.cv_digital_id.certificate_ids.filtered(
                lambda x: x.documentary_validation_state == 'validated')

    def unlink(self):
        self.mapped('cv_digital_id').write({'is_docket': False, 'is_docket_active': False})
        return super(ONSCLegajo, self).unlink()

    # REPORT UTILITIES
    def _get_contracts_sorted(self, only_most_recent=False):
        contracts_sorted = self.contract_ids.sorted(key=lambda contract_id: (
            _CUSTOM_ORDER.get(contract_id.legajo_state, 10),
            -to_timestamp(contract_id.date_start)
        ))
        if only_most_recent and len(contracts_sorted):
            return contracts_sorted[0]
        else:
            return contracts_sorted

    def _get_contract_active_job(self, contract_id):
        active_jobs = contract_id.job_ids.filtered(lambda x: x.end_date is False or x.end_date > fields.Date.today())
        if len(active_jobs):
            active_job = active_jobs[0]
            oldest_start_date = active_job.start_date
            for job in contract_id.job_ids.sorted(key=lambda job_id: (
                    -to_timestamp(job_id.start_date))):
                if job.id != active_job.id and job.department_id == active_job.department_id and job.end_date and (
                        oldest_start_date - job.end_date).days in [0, 1]:
                    oldest_start_date = job.start_date
            return {'job_id': active_jobs[0], 'oldest_start_date': oldest_start_date.strftime('%d/%m/%Y')}
        return {'job_id': active_jobs, 'oldest_start_date': False}

    def _get_report_legajo_formation_seccion(self):
        result = {}
        report_cv_seccions = []
        formations = self.advanced_formation_ids
        seccions = formations.mapped('advanced_study_level_id')
        seccions = sorted(seccions, key=lambda x: x.report_cv_order)
        for seccion in seccions:
            if seccion.report_cv_seccion not in report_cv_seccions:
                result[seccion.report_cv_seccion] = formations.filtered(
                    lambda x: x.advanced_study_level_id.report_cv_seccion == seccion.report_cv_seccion)
                report_cv_seccions.append(seccion.report_cv_seccion)
        return result

    def _get_vote_registry_details(self):
        result = []
        for vote_registry in self.vote_registry_ids:
            for electoral_act in vote_registry.electoral_act_ids:
                result.append({
                    'electoral_act': electoral_act.display_name,
                    'date': vote_registry.date.strftime('%d/%m/%Y')
                })
        return result

    def update_all_legajo_sections(self):
        cv = self.cv_digital_id.sudo().with_context(
            ignore_base_restrict=True,
            ignore_documentary_status=True
        )
        if not cv:
            return True

        # Lista de nombres de campos a procesar
        field_names = [
            'basic_formation_ids',
            'advanced_formation_ids',
            'course_certificate_ids',
            'other_relevant_information_ids',
            'participation_event_ids',
            'publication_production_evaluation_ids',
            'tutoring_orientation_supervision_ids',
            'volunteering_ids',
            'work_experience_ids',
            'work_investigation_ids',
            'work_teaching_ids'
        ]

        def process_validated_records(records):
            for record in records.filtered(lambda x: x.documentary_validation_state == 'validated'):
                record.set_legajo_validated_records()

        for field_name in field_names:
            records = getattr(cv, field_name)
            process_validated_records(records)

        return True
