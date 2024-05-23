# -*- coding: utf-8 -*-
from odoo import Command
from odoo import fields, models

WE_HISTORY_COLUMNS = [
    'country_id',
    'institution_id',
    'subinstitution_id',
    'currently_working',
    'start_date',
    'end_date',
    'position',
    'position_type',
    'is_full_time',
    'is_paid_activity',
    'professional_link_id',
    'responsible_type',
    'hours_worked_monthly',
    'other_relevant_information'
]
WE_TREE_HISTORY_COLUMNS = {
    'start_date': 'Inicio',
    'end_date': 'Fin',
    'professional_link_id': 'Vínculo profesional',
    'institution_id': 'Institución',
    'subinstitution_id': 'Sub institución',
    'hours_worked_monthly': 'Horas trabajadas al mes',
}


class ONSCCVDigitalWorkExperience(models.Model):
    _inherit = 'onsc.cv.work.teaching'
    _legajo_model = 'onsc.legajo.work.teaching'

    def _update_legajo_record_vals(self, vals):
        if 'subject_ids' in vals:
            vals['subject_ids'] = [Command.clear()] + vals['subject_ids']
        if 'education_area_ids' in vals:
            vals['education_area_ids'] = [Command.clear()] + vals['education_area_ids']
        if 'receipt_ids' in vals:
            vals['receipt_ids'] = [Command.clear()] + vals['receipt_ids']
        return vals


class ONSCLegajoWorkTeaching(models.Model):
    _name = 'onsc.legajo.work.teaching'
    _inherit = ['onsc.cv.work.teaching', 'model.history']
    _description = 'Legajo - Docencia'
    _history_model = 'onsc.legajo.work.teaching.history'
    _history_columns = WE_HISTORY_COLUMNS
    _tree_history_columns = WE_TREE_HISTORY_COLUMNS

    employee_id = fields.Many2one("hr.employee", string=u"Funcionario")
    legajo_id = fields.Many2one("onsc.legajo", string=u"Legajo")
    origin_record_id = fields.Many2one(
        "onsc.cv.work.teaching",
        string=u"Docencia origen",
        ondelete="set null")

    # Grilla Materias
    subject_ids = fields.One2many('onsc.legajo.academic.program.subject', inverse_name='legajo_work_teaching_id',
                                  string='Materias')
    # Grilla Áreas relacionadas con esta educación
    education_area_ids = fields.One2many('onsc.legajo.education.area.teaching', inverse_name='legajo_work_teaching_id',
                                         string="Áreas relacionadas con esta educación")
    # Grila Comprobantes
    receipt_ids = fields.One2many('onsc.legajo.work.teaching.receipt.file', inverse_name='legajo_work_teaching_id',
                                  string='Comprobantes')

    def button_show_history(self):
        model_view_form_id = self.env.ref('onsc_cv_digital_legajo.onsc_legajo_work_teaching_form').id
        return self.with_context(model_view_form_id=model_view_form_id,
                                 as_of_date=fields.Date.today()).get_history_record_action(
            history_id=False,
            res_id=self.id,
        )


class ONSCLegajoAcademicProgramSubject(models.Model):
    _name = 'onsc.legajo.academic.program.subject'
    _inherit = 'onsc.cv.academic.program.subject'
    _description = 'Legajo - Materias'

    legajo_work_teaching_id = fields.Many2one(
        "onsc.legajo.work.teaching",
        string="Docencia",
        ondelete='cascade'
    )

    knowledge_acquired_ids = fields.Many2many(
        'onsc.cv.knowledge',
        relation='legajo_knowledge_teaching_program_rel',
        string='Conocimientos enseñados',
        required=True,
        ondelete='restrict', )


class ONSCLegajoEducationAreaTeaching(models.Model):
    _name = 'onsc.legajo.education.area.teaching'
    _inherit = 'onsc.cv.education.area.teaching'
    _description = 'Legajo - Materias'

    legajo_work_teaching_id = fields.Many2one(
        "onsc.legajo.work.teaching",
        string="Docencia",
        ondelete='cascade'
    )


class ONSCLegajoWorkTeachingReceiptFile(models.Model):
    _name = 'onsc.legajo.work.teaching.receipt.file'
    _inherit = 'onsc.cv.work.teaching.receipt.file'
    _description = 'Legajo - Comprobantes'

    legajo_work_teaching_id = fields.Many2one(
        "onsc.legajo.work.teaching",
        string="Docencia",
        ondelete='cascade'
    )


# HISTORICOS
class ONSCLegajoWorkTeachingHistory(models.Model):
    _name = 'onsc.legajo.work.teaching.history'
    _inherit = ['model.history.data']
    _parent_model = 'onsc.legajo.work.teaching'
