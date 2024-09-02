# -*- coding: utf-8 -*-

from odoo import Command
from odoo import fields, models

POSTGRADUATE_TYPES = [('academic', 'Académico'), ('professional', 'Profesional')]
HISTORY_COLUMNS = [
    'start_date',
    'end_date',
    'work_title',
    'tutor_type_id',
    'country_id',
    'institution_id',
    'subinstitution_id',
    'dependence',
    'academic_program_id',
    'postgraduate_type',
    'student_name',
    'language_id',
    'divulgation_media_id',
    'website',
    'orientation_type_id',
    'is_paid_activity',
    'is_relevant_work',
    'is_tutoring_finished',
    'other_tutor_type',
    'co_tutor_name',
    'other_divulgation_media',
    'receipt_file',
    'receipt_filename',
    'other_relevant_information',
    'description',
    'knowledge_acquired_ids',
    # HISTORICOS
    'documentary_validation_date',
    'documentary_validation_state',
    'documentary_user_id',
    'generic_academic_program_id',
    'name_generic_academic_program'
]
TREE_HISTORY_COLUMNS = [
    'start_date',
    'end_date',
    'work_title',
    'tutor_type_id',
    'country_id',
    'institution_id',
    'subinstitution_id',
    'dependence',
    'academic_program_id',
    'postgraduate_type',
    'student_name',
    'language_id',
    'divulgation_media_id',
    'website',
    'orientation_type_id',
    'is_paid_activity',
    'is_relevant_work',
]


class ONSCCVTutorialOrientationSupervision(models.Model):
    _inherit = 'onsc.cv.tutoring.orientation.supervision'
    _legajo_model = 'onsc.legajo.tutoring.orientation.supervision'

    def _update_legajo_record_vals(self, vals):
        if 'area_ids' in vals:
            vals['area_ids'] = [Command.clear()] + vals['area_ids']
        if 'knowledge_acquired_ids' in vals:
            vals['knowledge_acquired_ids'] = [Command.clear()] + vals['knowledge_acquired_ids']
        return vals


class ONSCLegajoTutorialOrientationSupervision(models.Model):
    _name = 'onsc.legajo.tutoring.orientation.supervision'
    _description = 'Legajo - Tutorías, Orientaciones, Supervisiones'
    _inherit = ['onsc.cv.tutoring.orientation.supervision', 'model.history']
    _history_model = 'onsc.legajo.tutoring.orientation.supervision.history'
    _history_columns = HISTORY_COLUMNS
    _tree_history_columns = TREE_HISTORY_COLUMNS
    _order = 'start_date desc'

    employee_id = fields.Many2one("hr.employee", string=u"Funcionario")
    legajo_id = fields.Many2one("onsc.legajo", string=u"Legajo")
    origin_record_id = fields.Many2one(
        "onsc.cv.tutoring.orientation.supervision",
        string=u"Experiencia laboral origen",
        ondelete="set null"
    )

    area_ids = fields.One2many('onsc.legajo.education.area.tutoring', 'legajo_tutoring_id', 'Área de actividad', copy=True)
    knowledge_acquired_ids = fields.Many2many(
        'onsc.cv.knowledge',
        relation='legajo_knowledge_acquired_tutoring_rel',
        string='Conocimientos aplicados',
        required=True,
        ondelete='restrict', )
    is_orientation_type_pie = fields.Boolean(string="Es tipo de orientacion pie ? ", history=True)
    is_tutor_docent = fields.Boolean(string="Es Docente tutor ? ", history=True)
    is_tutor_master = fields.Boolean(string="Es tutor? ", history=True)
    is_tutor_option_other_enable = fields.Boolean(string='Permitir opción otra/o?', history=True)
    is_divulgation_option_other_enable = not fields.Boolean(string='Otro medio de divulgación?', history=True)
    show_generic_academic_program = fields.Boolean('¿Ver programa academico generico?', history=True)
    displayed_academic_program = fields.Char(string='Programa académico', history=True)

    def button_show_history(self):
        model_view_form_id = self.env.ref('onsc_cv_digital_legajo.onsc_legajo_tutoring_orientation_supervision_form').id
        return self.with_context(model_view_form_id=model_view_form_id,
                                 as_of_date=fields.Date.today()).get_history_record_action(
            history_id=False,
            res_id=self.id,
        )


class ONSCLegajoEducationAreaTutorial(models.Model):
    _name = 'onsc.legajo.education.area.tutoring'
    _inherit = ['onsc.cv.education.area.tutoring']
    _description = 'Legajo -  Áreas relacionadas con esta educación (tutorías, orientaciones, supervisiones)'

    legajo_tutoring_id = fields.Many2one(
        'onsc.legajo.tutoring.orientation.supervision',
        'Tutoría, Orientación, Supervisión',
        ondelete='cascade',
        required=False)
    tutoring_id = fields.Many2one(
        'onsc.cv.tutoring.orientation.supervision',
        'Tutoría, Orientación, Supervisión',
        ondelete='cascade', required=False)


# HISTORICO
class ONSCLegajoTutorialOrientationSupervisionHistory(models.Model):
    _name = 'onsc.legajo.tutoring.orientation.supervision.history'
    _inherit = ['model.history.data']
    _parent_model = 'onsc.legajo.tutoring.orientation.supervision'

    history_receipt_file = fields.Binary(string="Comprobante")
