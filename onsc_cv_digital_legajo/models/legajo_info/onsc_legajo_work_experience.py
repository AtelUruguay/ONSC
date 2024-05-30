# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError
# CAMPOS A GUARDAR EN HISTORICO. UTIL PARA EN HERENCIAS NO REPETIR CAMPOS PARA SOLO PONER history=True
HISTORY_COLUMNS = [
    'position',
    'country_id',
    'city_id',
    'start_date',
    'currently_working',
    'end_date',
    'company_type',
    'country_code',
    'unit_name',
    'entry_institution_id',
    'hierarchical_level_id',
    'take_decisions',
    'is_paid_activity',
    'people_charge_qty',
    'organizational_units_charge',
    'hours_worked_monthly',
    'receipt_file',
    'receipt_filename',
    'description_tasks',
    'causes_discharge',
    'inciso_id',
    'operating_unit_id',
    'company_name_calc',
    # HISTORICOS
    'documentary_validation_date',
    'documentary_validation_state',
    'documentary_user_id'
]
# ELEMENTOS A MOSTRAR EN LA VISTA LISTA (RESPETA EL ORDEN)
TREE_HISTORY_COLUMNS = {
    'start_date': 'Inicio',
    'end_date': 'Fin',
    'position': 'Cargo desempeñado',
    'company_name_calc': 'Empresa',
    'unit_name': 'Área/Unidad',
}


class ONSCLegajoWorkExperience(models.Model):
    _name = 'onsc.legajo.work.experience'
    _inherit = ['onsc.cv.work.experience', 'model.history']
    _description = 'Legajo - Experiencia laboral'
    _history_model = 'onsc.legajo.work.experience.history'
    _history_columns = HISTORY_COLUMNS
    _tree_history_columns = TREE_HISTORY_COLUMNS

    employee_id = fields.Many2one("hr.employee", string=u"Funcionario")
    legajo_id = fields.Many2one("onsc.legajo", string=u"Legajo")
    origin_record_id = fields.Many2one(
        "onsc.cv.work.experience",
        string=u"Experiencia laboral origen",
        ondelete="set null")

    company_name_calc = fields.Char('Empresa', history=True)

    task_ids = fields.One2many(
        "onsc.legajo.work.experience.task",
        inverse_name="legajo_work_experience_id",
        string="Tareas",
        # history_fields="key_task_id,area_id"
    )

    def button_show_history(self):
        model_view_form_id = self.env.ref('onsc_cv_digital_legajo.onsc_legajo_work_experience_form_view').id
        return self.with_context(model_view_form_id=model_view_form_id,
                                 as_of_date=fields.Date.today()).get_history_record_action(
            history_id=False,
            res_id=self.id,
        )


class ONSCLegajoWorkExperienceTask(models.Model):
    _name = 'onsc.legajo.work.experience.task'
    _inherit = 'onsc.cv.work.experience.task'
    _description = 'Legajo - Tareas de experiencia laboral'

    legajo_work_experience_id = fields.Many2one(
        "onsc.legajo.work.experience",
        string="Experiencia laboral",
        ondelete='cascade'
    )


# HISTORICOS
class ONSCLegajoWorkExperienceHistory(models.Model):
    _name = 'onsc.legajo.work.experience.history'
    _inherit = ['model.history.data']
    _parent_model = 'onsc.legajo.work.experience'

    history_receipt_file = fields.Binary(string="Comprobante")
