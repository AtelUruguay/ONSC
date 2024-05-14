# -*- coding: utf-8 -*-

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
    'other_tutor_type'
    'co_tutor_name'
    'other_divulgation_media'
    'receipt_file'
    'receipt_filename'
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

class ONSCLegajoTutorialOrientationSupervision(models.Model):
    _name = 'onsc.legajo.tutoring.orientation.supervision'
    _description = 'Legajo - Tutorías, Orientaciones, Supervisiones'
    _inherit = ['onsc.cv.tutoring.orientation.supervision']
    _history_model = 'onsc.legajo.tutoring.orientation.supervision.history'
    _history_columns = HISTORY_COLUMNS
    _tree_history_columns = TREE_HISTORY_COLUMNS
    _order = 'start_date desc'


class ONSCLegajoEducationAreaTutorial(models.Model):
    _name = 'onsc.legajo.education.area.tutoring'
    _inherit = ['onsc.cv.education.area.tutoring']
    _description = 'Legajo -  Áreas relacionadas con esta educación (tutorías, orientaciones, supervisiones)'


# HISTORICO
class ONSCLegajoTutorialOrientationSupervisionHistory(models.Model):
    _name = 'onsc.legajo.tutoring.orientation.supervision.history'
    _inherit = ['model.history.data']
    _parent_model = 'onsc.legajo.tutoring.orientation.supervision'

    history_receipt_file = fields.Binary(string="Comprobante")