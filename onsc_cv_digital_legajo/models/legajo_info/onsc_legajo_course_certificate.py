# -*- coding: utf-8 -*-
from odoo import Command
from odoo import fields, models

HISTORY_COLUMNS = [
    'course_type',
    'course_title',
    'country_id',
    'institution_id',
    'subinstitution_id',
    'approbation_mode',
    'evaluation_number',
    'evaluation_max_str',
    'evaluation_max_number',
    'state',
    'start_date',
    'end_date',
    'induction_type',
    'dictation_mode',
    'hours_total',
    'digital_doc_file',
    'digital_doc_filename',
    'other_relevant_information',
    'evaluation_str',
    'knowledge_acquired_ids',
    # HISTORICOS
    'documentary_validation_date',
    'documentary_validation_state',
    'documentary_user_id'
]

TREE_HISTORY_COLUMNS = {
    'start_date': 'Inicio',
    'end_date': 'Fin',
    'course_type': 'Tipo',
    'course_title': 'Titulo',
    'state': 'Estado',
    'institution_id': 'Institución',
    'subinstitution_id': 'Sub institución',
}


class ONSCCVDigitalLegajoCourseCertificate(models.Model):
    _inherit = 'onsc.cv.course.certificate'
    _legajo_model = 'onsc.legajo.course.certificate'
    _order = 'start_date desc'

    def _update_legajo_record_vals(self, vals):
        if 'line_ids' in vals:
            vals['line_ids'] = [Command.clear()] + vals['line_ids']
        return vals


class ONSCLegajoCourseCertificate(models.Model):
    _name = 'onsc.legajo.course.certificate'
    _inherit = ['onsc.cv.course.certificate', 'model.history']
    _description = 'Legajo - Cursos y certificados'
    _history_model = 'onsc.legajo.course.certificate.history'
    _history_columns = HISTORY_COLUMNS
    _tree_history_columns = TREE_HISTORY_COLUMNS

    employee_id = fields.Many2one("hr.employee", string=u"Funcionario")
    legajo_id = fields.Many2one("onsc.legajo", string=u"Legajo")
    origin_record_id = fields.Many2one(
        "onsc.cv.course.certificate",
        string=u"Cursos y certificados origen",
        ondelete="set null"
    )

    line_ids = fields.One2many('onsc.legajo.education.area.course', inverse_name='legajo_investigation_id',
                               copy=True,
                               string="Áreas relacionadas con esta educación")
    knowledge_acquired_ids = fields.Many2many('onsc.cv.knowledge', 'legajo_knowledge_acquired_course_rel',
                                              string=u'Conocimientos adquiridos',
                                              required=True,
                                              copy=True,
                                              ondelete='restrict',
                                              store=True)
    is_numeric_max_evaluation = fields.Boolean(string="Es numerico nota maxima?", history=True)
    is_numeric_evaluation = fields.Boolean(string="Es numerico nota?", history=True)

    def button_show_history(self):
        model_view_form_id = self.env.ref('onsc_cv_digital_legajo.onsc_legajo_course_certificate_form').id
        return self.with_context(model_view_form_id=model_view_form_id,
                                 as_of_date=fields.Date.today()).get_history_record_action(
            history_id=False,
            res_id=self.id,
        )


class ONSCLegajoEducationAreaCourse(models.Model):
    _name = 'onsc.legajo.education.area.course'
    _inherit = 'onsc.cv.education.area.course'
    _description = 'Legajo - Áreas relacionadas con esta educación'

    legajo_investigation_id = fields.Many2one(
        "onsc.legajo.course.certificate",
        string="Cursos y certificados",
        ondelete='cascade'
    )


class ONSCLegajoCourseCertificateHistory(models.Model):
    _name = 'onsc.legajo.course.certificate.history'
    _inherit = ['model.history.data']
    _parent_model = 'onsc.legajo.course.certificate'

    history_digital_doc_file = fields.Binary(string="Certificado/constancia")
