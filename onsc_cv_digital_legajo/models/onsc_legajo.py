# -*- coding: utf-8 -*-

from odoo import models, fields


class ONSCLegajo(models.Model):
    _inherit = "onsc.legajo"

    cv_digital_id = fields.Many2one(
        comodel_name="onsc.cv.digital",
        related='employee_id.cv_digital_id', store=True)

    # FORMACION

    basic_formation_ids = fields.One2many(
        'onsc.legajo.basic.formation', string=u'Formación básica', inverse_name="legajo_id",)
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

    def _compute_formations(self):
        for record in self:
            record.certificate_ids = record.cv_digital_id.certificate_ids.filtered(
                lambda x: x.documentary_validation_state == 'validated')

    def unlink(self):
        self.mapped('cv_digital_id').write({'is_docket': False, 'is_docket_active': False})
        return super(ONSCLegajo, self).unlink()
