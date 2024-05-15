# -*- coding: utf-8 -*-

from odoo import models, fields


class ONSCLegajo(models.Model):
    _inherit = "onsc.legajo"

    cv_digital_id = fields.Many2one(
        comodel_name="onsc.cv.digital",
        related='employee_id.cv_digital_id', store=True)

    # FORMACION
    basic_formation_ids = fields.One2many(
        'onsc.cv.basic.formation', string=u'Formación básica',
        compute='_compute_formations',
        compute_sudo=True)
    advanced_formation_ids = fields.One2many(
        'onsc.cv.advanced.formation', string=u'Formación avanzada',
        compute='_compute_formations',
        compute_sudo=True)

    # CURSOS Y CERTIFICADOS
    course_ids = fields.One2many(
        'onsc.cv.course.certificate',
        string="Cursos",
        compute='_compute_formations',
        compute_sudo=True)
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
    volunteering_ids = fields.One2many(
        "onsc.legajo.volunteering",
        inverse_name="legajo_id",
        string="Voluntariado"
    )

    def _compute_formations(self):
        for record in self:
            record.advanced_formation_ids = record.cv_digital_id.advanced_formation_ids.filtered(
                lambda x: x.documentary_validation_state == 'validated')
            record.basic_formation_ids = record.cv_digital_id.basic_formation_ids.filtered(
                lambda x: x.documentary_validation_state == 'validated')
            record.course_ids = record.cv_digital_id.course_ids.filtered(
                lambda x: x.documentary_validation_state == 'validated')
            record.certificate_ids = record.cv_digital_id.certificate_ids.filtered(
                lambda x: x.documentary_validation_state == 'validated')

    def unlink(self):
        self.mapped('cv_digital_id').write({'is_docket': False, 'is_docket_active': False})
        return super(ONSCLegajo, self).unlink()
