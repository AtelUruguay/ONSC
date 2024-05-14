# -*- coding: utf-8 -*-
from odoo import fields, models

WE_HISTORY_COLUMNS = [
    'company_type',
    'country_id',
    'start_date',
    'currently_volunteering',
    'unit_name',
    'hours_monthly',
    'receipt_description',
    'receipt_file',
    'receipt_filename',
    'description_tasks',
    'inciso_id',
    'operating_unit_id'
]

WE_TREE_HISTORY_COLUMNS = [
    'start_date',
    'end_date',
    'company_type',
    'company_name_calc',
    'unit_name',
    'country_id',
    'hours_monthly',
]



class ONSCCVDigitalVolunteering(models.Model):
    _name = 'onsc.legajo.work.teaching'
    _inherit = ['onsc.cv.work.teaching', 'model.history']
    _description = 'Legajo - Docencia'
    _history_model = 'onsc.legajo.work.teaching.history'
    _history_columns = WE_HISTORY_COLUMNS
    _tree_history_columns = WE_TREE_HISTORY_COLUMNS

    employee_id = fields.Many2one("hr.employee", string=u"Funcionario")
    legajo_id = fields.Many2one("onsc.legajo", string=u"Legajo")
    origin_record_id = fields.Many2one("onsc.cv.volunteering", string=u"Voluntariado origen")

    # Grilla Materias
    subject_ids = fields.One2many('onsc.legajo.academic.program.subject', 'legajo_work_teaching_id', string='Materias')
    # Grilla Áreas relacionadas con esta educación
    education_area_ids = fields.One2many('onsc.legajo.education.area.teaching', inverse_name='legajo_work_teaching_id',
                                         string="Áreas relacionadas con esta educación")
      # Grila Comprobantes
    receipt_ids = fields.One2many('onsc.cv.work.teaching.receipt.file', inverse_name='legajo_work_teaching_id',
                                  string='Comprobantes')


    def button_show_history(self):
        model_view_form_id = self.env.ref('onsc_cv_digital_legajo.onsc_legajo_volunteering_form_view').id
        return self.with_context(model_view_form_id=model_view_form_id,
                                 as_of_date=fields.Date.today()).get_history_record_action(
            history_id=False,
            res_id=self.id,
        )

class ONSCLegajoVolunteeringTask(models.Model):
    _name = 'onsc.legajo.academic.program.subject'
    _inherit = 'onsc.cv.academic.program.subject'
    _description = 'Legajo - Materias'

    legajo_work_teaching_id = fields.Many2one(
        "onsc.legajo.work.teaching",
        string="Docencia",
        ondelete='cascade'
    )

class ONSCLegajoVolunteeringTask(models.Model):
    _name = 'onsc.legajo.education.area.teaching'
    _inherit = 'onsc.cv.education.area.teaching'
    _description = 'Legajo - Materias'

    legajo_work_teaching_id = fields.Many2one(
        "onsc.legajo.work.teaching",
        string="Docencia",
        ondelete='cascade'
    )

class ONSCLegajoVolunteeringTask(models.Model):
    _name = 'onsc.legajo.work.teaching.receipt.file'
    _inherit = 'onsc.cv.work.teaching.receipt.file'
    _description = 'Legajo - Comprobantes'

    legajo_work_teaching_id = fields.Many2one(
        "onsc.legajo.work.teaching",
        string="Docencia",
        ondelete='cascade'
    )


